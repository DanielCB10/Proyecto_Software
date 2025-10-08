<?php

namespace App\Jobs;

use App\Mail\OperationNotification;
use Exception;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Log;

class SendOperationEmail implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $email;
    public $data;

    public $tries = 3;

    public function __construct(string $email, array $data)
    {
        $this->email = $email;
        $this->data = $data;
    }

    public function handle()
    {
        Mail::to($this->email)->send(new OperationNotification($this->data));
    }

    public function failed(Exception $exception)
    {
        // Guardar el error en logs para debugging
        Log::error('SendOperationEmail failed', [
            'email' => $this->email,
            'error' => $exception->getMessage()
        ]);
    }
}
