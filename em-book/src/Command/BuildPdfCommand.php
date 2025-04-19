<?php

/*
 * This file is part of the markdown book project template.
 *
 * (c) Carl Alexander <contact@carlalexander.ca>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

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
use Illuminate\Support\Facades\App;

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

        $princeFile = 'output/output.pdf';
        $samples = [
            'output/book.pdf' => [1] + range(2, 33),
            'output/sample.pdf' => [1, 2, 10, 11, 12, 13],
        ];

        $preface = $this->generateMarkdownHtml('content', '0-*.md');
        $section1 = $this->generateMarkdownHtml('content', '1-*.md');
        $section2 = $this->generateMarkdownHtml('content', '2-*.md');
        $section3 = $this->generateMarkdownHtml('content', '3-*.md');
        $section4 = $this->generateMarkdownHtml('content', '4-*.md');
        $section5 = $this->generateMarkdownHtml('content', '5-*.md');
        $section6 = $this->generateMarkdownHtml('content', '6-*.md');
        $section7 = $this->generateMarkdownHtml('content', '7-*.md');
        $section8 = $this->generateMarkdownHtml('content', '8-*.md');

        $contents = $this->generateTableOfContentsHtml($preface).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section1).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section2).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section3).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section4).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section5).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section6).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section7).'<div class="separator">∫</div>'
                  . $this->generateTableOfContentsHtml($section8);

        file_put_contents('output/output.html', $this->twig->render('book.html.twig', [
            'contents' => $contents,
            'preface' => $preface,
            'section1' => $section1,
            'section2' => $section2,
            'section3' => $section3,
            'section4' => $section4,
            'section5' => $section5,
            'section6' => $section6,
            'section7' => $section7,
            'section8' => $section8,
        ]));

        $process = new Process(['prince', 'output/output.html', '--javascript', '-o', $princeFile]);
        $result = $process->run();

        foreach ($samples as $sampleFile => $samplePages) {
            $this->createPdf($princeFile, $sampleFile, $samplePages);
        }

        return $result;
    }

    private function createPdf($sourceFile, $outputFile, array $pages)
    {
        $pdf = new Fpdi();
        $pdf->setSourceFile($sourceFile);

        foreach ($pages as $page) {
            $pageId = $pdf->importPage($page);
            $size = $pdf->getTemplateSize($pageId);

            $pdf->AddPage($size['orientation'], $size);

            $pdf->useTemplate($pageId);
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
