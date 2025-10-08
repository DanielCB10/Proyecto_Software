@component('mail::message')
# {{ $data['title'] ?? 'Notificación' }}

Hola {{ $data['user_name'] ?? 'Usuario' }},

Se ha realizado la siguiente operación en tu cuenta **{{ $data['account_number'] ?? '-' }}**:

- **Tipo:** {{ $data['type'] ?? '-' }}
- **Monto:** {{ $data['amount_formatted'] ?? '-' }}
- **Saldo actual:** {{ $data['new_balance_formatted'] ?? '-' }}
- **Referencia:** {{ $data['reference'] ?? 'N/A' }}
- **Fecha:** {{ $data['date'] ?? '-' }}

Gracias por usar nuestro servicio.
@endcomponent
