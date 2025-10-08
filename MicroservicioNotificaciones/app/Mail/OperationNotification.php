<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Queue\SerializesModels;

class OperationNotification extends Mailable
{
    use Queueable, SerializesModels;

    public $data; // datos que pasaremos a la vista

    public function __construct(array $data)
    {
        $this->data = $data;
    }

    public function build()
    {
        return $this->subject($this->data['subject'] ?? 'Notificación de operación')
                    ->markdown('emails.operation_notification', ['data' => $this->data]);
    }
}
