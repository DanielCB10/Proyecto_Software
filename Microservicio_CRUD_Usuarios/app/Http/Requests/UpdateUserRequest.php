<?php


namespace App\Http\Requests;


use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;


class UpdateUserRequest extends FormRequest
{
public function authorize(): bool
{
return true;
}


public function rules(): array
{
$userId = $this->route('user');


return [
'name' => 'sometimes|required|string|max:120',
'email' => ['sometimes','required','email', Rule::unique('users','email')->ignore($userId)],
'password' => 'nullable|string|min:6',
'role' => 'nullable|string',
'status' => 'nullable|string',
];
}
}