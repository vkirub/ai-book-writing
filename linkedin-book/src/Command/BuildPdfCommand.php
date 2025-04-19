<?php
namespace App\Command;

use App\Collection;
use App\Markdown\Parsedown;
use setasign\Fpdi\Fpdi;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\DomCrawler\Crawler;
use Symfony\Component\Finder\Finder;
use Symfony\Component\Process\Process;
use Twig\Environment;
use Symfony\Component\Yaml\Yaml;

/**
 * Command for building the book PDF.
 *
 * @author Carl Alexander <contact@carlalexander.ca>
 */
class BuildPdfCommand extends Command
{
    /**
     * Markdown parser
     *
     * @var Parsedown
     */
    private $parser;

    /**
     * @var Environment
     */
    private $twig;

    /**
     * Constructor.
     *
     * @param Parsedown   $parser
     * @param Environment $twig
     */
    public function __construct(Parsedown $parser, Environment $twig)
    {
        parent::__construct('book:build-pdf');

        $this->parser = $parser;
        $this->twig = $twig;
    }

    /**
     * {@inheritdoc}
     */
    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $data = Yaml::parseFile('content/book.yaml');

        $outputpdf = $data['output']['pdf'];
        $outputhtml = $data['output']['html'];
        $bookpdf = $data['output']['book']['pdf'];
        $samplepdf = $data['output']['sample']['pdf'];


        $max_pages = $data['output']['book']['max_pages'];
        $samplePagesStr = $data['output']['sample']['pages'];
        $title = $data['title'];
        $subtitle = $data['subtitle'];
        $authors = $data['authors'];
        $website = $data['website'];
        $css = $data['css'];


        $samplesArray = array_map('intval', explode(',', $samplePagesStr));
        $princeFile = $outputpdf;
        $samples = [
            $bookpdf => [1] + range(2, $max_pages),
            $samplepdf => $samplesArray,
        ];

        $markDownSections = $data['sections'];
        $htmlSections = [];
        $tocEntry = [];
            foreach ($markDownSections as $key => $value) {
                print $key;
            $htmlContent = $this->generateMarkdownHtml('content', $value);
            $htmlSections[$key] = $htmlContent;
            $tocEntry[$key] = $this->generateTableOfContentsHtml($htmlContent);
        }        

        $sep = '<div class="separator">∫</div>';

        $contents = implode($sep, $tocEntry);

        file_put_contents($outputhtml, $this->twig->render('book.html.twig', [
            'contents' => $contents,
            'preface' => $htmlSections['preface'] ?? '',
            'section1' => $htmlSections['section1'] ?? '',
            'section2' => $htmlSections['section2'] ?? '',
            'section3' => $htmlSections['section3'] ?? '',
            'section4' => $htmlSections['section4'] ?? '',
            'section5' => $htmlSections['section5'] ?? '',
            'section6' => $htmlSections['section6'] ?? '',
            'section7' => $htmlSections['section7'] ?? '',
            'section8' => $htmlSections['section8'] ?? '',
            'section9' => $htmlSections['section9'] ?? '',
            'title' => $title,
            'subtitle' => $subtitle,
            'authors' => $authors,
            'website' => $website,
            'css' => $css
        ]));

        $process = new Process(['prince', $outputhtml, '--javascript', '-o', $princeFile]);
        $result = $process->run();

        foreach ($samples as $sampleFile => $samplePages) {
            $this->createPdf($princeFile, $sampleFile, $samplePages);
        }

        return $result;
    }

    private function createPdf($sourceFile, $outputFile, array $pages)
    {
        $pdf = new Fpdi();
        $pageCount = $pdf->setSourceFile($sourceFile);
        foreach ($pages as $page) {
            if ($page <= $pageCount) {
            $pageId = $pdf->importPage($page);
            $size = $pdf->getTemplateSize($pageId);

            $pdf->AddPage($size['orientation'], $size);

            $pdf->useTemplate($pageId);
            }
        }

        $pdf->output('F', $outputFile);
    }

    private function generateHeadingsHtml(Collection $headings)
    {
        return '<ul>'.$headings->map(function(array $heading) {
            $html = '<li>'.sprintf('<a href="#%s">%s</a>', $heading['id'], $heading['title']);

            if (!$heading['children']->isEmpty()) {
                $html .= $this->generateHeadingsHtml($heading['children']);
            }

            return $html.'</li>';
        })->implode('').'</ul>';
    }

    private function generateMarkdownHtml($path, $extension)
    {
        $html = '';
        $files = Finder::create()->files()->in($path)->name($extension)->depth(0)->sortByName();

        foreach ($files as $file) {
            $html .= $this->parser->text($file->getContents());
        }

        return $html;
    }

    private function generateTableOfContentsHtml($html)
    {
        $crawler = (new Crawler($html))->filter('h1, h2');
        $headings = new Collection();

        foreach ($crawler as $element) {
            $headings->push([
                'level' => (int) ltrim($element->nodeName, 'h'),
                'title' => $element->textContent,
                'id' => $element->getAttribute('id'),
            ]);
        }

        $headings = $this->groupHeadingsByLevel($headings);

        return $this->generateHeadingsHtml($headings);
    }

    private function groupHeadingsByLevel(Collection $headings, $level = 1)
    {
        return $headings->chunkWhen(function(array $heading) use ($level) {
            return $level === $heading['level'];
        })->map(function(Collection $headings) use ($level) {
            $heading = $headings->shift();
            $heading['children'] = $this->groupHeadingsByLevel($headings, $level + 1);

            return $heading;
        });
    }
}
