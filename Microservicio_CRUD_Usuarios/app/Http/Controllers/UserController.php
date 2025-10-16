<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Http\Requests\StoreUserRequest;
use App\Http\Requests\UpdateUserRequest;
// use App\Http\Requests\ChangePasswordRequest; // Descomenta si lo usas
use App\Http\Resources\UserResource;
use Illuminate\Support\Facades\Hash;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

class UserController extends Controller
{
    // Lista con paginación y filtro simple
    public function index(Request $request)
    {
        $perPage = $request->query('per_page', 10);
        $q = $request->query('q');

        $query = User::query();

        if ($q) {
            $query->where(function ($qbuilder) use ($q) {
                $qbuilder->where('name', 'like', "%{$q}%")
                         ->orWhere('email', 'like', "%{$q}%");
            });
        }

        $users = $query->orderByDesc('id')->paginate($perPage);

        return UserResource::collection($users)->additional(['total' => $users->total()]);
    }

    public function show(User $user)
    {
        return new UserResource($user);
    }

    public function store(StoreUserRequest $request)
    {
        $data = $request->validated();
        $data['password'] = Hash::make($data['password']);

        $user = User::create($data);

        return (new UserResource($user))->response()->setStatusCode(Response::HTTP_CREATED);
    }

    public function update(UpdateUserRequest $request, User $user)
    {
        // Obtener los datos validados
        $data = $request->validated();

        // Si viene password, hashearla antes de guardar
        if (array_key_exists('password', $data) && $data['password'] !== null && $data['password'] !== '') {
            $data['password'] = Hash::make($data['password']);
        } else {
            // Si no incluye password en el payload, evitar sobreescribirlo
            unset($data['password']);
        }

        // Actualizar el usuario
        $user->update($data);

        // Devolver recurso actualizado (200 OK)
        return new UserResource($user);
    }

    public function destroy(User $user)
    {
        $user->delete();

        // 204 No Content es la respuesta habitual para borrados exitosos
        return response()->noContent();
    }
}
