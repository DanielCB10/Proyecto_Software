<?php


namespace App\Http\Resources;


use Illuminate\Http\Resources\Json\JsonResource;


class UserResource extends JsonResource
{
public function toArray($request): array
{
return [
'id' => $this->id,
'name' => $this->name,
'email' => $this->email,
'role' => $this->role,
'status' => $this->status,
'created_at' => $this->created_at?->toDateTimeString(),
'updated_at' => $this->updated_at?->toDateTimeString(),
'deleted_at' => $this->deleted_at?->toDateTimeString(),
];
}
}