<?php


namespace App\Http\Requests;


use Illuminate\Foundation\Http\FormRequest;


class StoreUserRequest extends FormRequest
{
public function authorize(): bool
{
return true; // Ajusta según tu auth
}


public function rules(): array
{
return [
'name' => 'required|string|max:120',
'email' => 'required|email|unique:users,email',
'password' => 'required|string|min:6',
'role' => 'nullable|string',
'status' => 'nullable|string',
];
}
}