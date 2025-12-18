#!/usr/bin/env php
<?php
/**
 * Cloudsmith Composer Auth Plugin
 * 
 * This plugin provides automatic authentication for Cloudsmith Composer repositories.
 * 
 * Installation:
 *   composer global require cloudsmith/composer-auth-plugin
 *   
 * Or add to your project:
 *   composer require --dev cloudsmith/composer-auth-plugin
 */

namespace Cloudsmith\ComposerAuth;

use Composer\Plugin\PluginInterface;
use Composer\Plugin\Capable;
use Composer\Composer;
use Composer\IO\IOInterface;

class Plugin implements PluginInterface, Capable
{
    public function activate(Composer $composer, IOInterface $io)
    {
        // Plugin activated
    }

    public function deactivate(Composer $composer, IOInterface $io)
    {
        // Plugin deactivated
    }

    public function uninstall(Composer $composer, IOInterface $io)
    {
        // Plugin uninstalled
    }

    public function getCapabilities()
    {
        return [
            'Composer\Plugin\Capability\CommandProvider' => CommandProvider::class,
        ];
    }
}

class CloudsmithAuth
{
    public static function getToken()
    {
        $oidcSlug = getenv('CLOUDSMITH_OIDC_SLUG');
        $cmd = ['cloudsmith', 'tokens', 'get'];
        
        if ($oidcSlug) {
            $cmd[] = '--oidc-slug';
            $cmd[] = $oidcSlug;
        }
        
        $process = proc_open(
            $cmd,
            [
                1 => ['pipe', 'w'],
                2 => ['pipe', 'w'],
            ],
            $pipes
        );
        
        if (is_resource($process)) {
            $token = stream_get_contents($pipes[1]);
            fclose($pipes[1]);
            fclose($pipes[2]);
            proc_close($process);
            
            return trim($token);
        }
        
        return null;
    }
}
