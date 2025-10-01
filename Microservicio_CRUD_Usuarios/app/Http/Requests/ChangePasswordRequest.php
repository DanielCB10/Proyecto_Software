<?php


namespace App\Http\Requests;


use Illuminate\Foundation\Http\FormRequest;


class ChangePasswordRequest extends FormRequest
{
public function authorize(): bool
{
return true;
}


public function rules(): array
{
return [
'new_password' => 'required|string|min:6',
];
}
}