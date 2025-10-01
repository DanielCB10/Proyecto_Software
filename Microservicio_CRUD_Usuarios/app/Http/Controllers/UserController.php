<?php


namespace App\Http\Controllers;


use App\Http\Controllers\Controller;
use App\Models\User;
use App\Http\Requests\StoreUserRequest;
use App\Http\Requests\UpdateUserRequest;
use App\Http\Requests\ChangePasswordRequest;
use App\Http\Resources\UserResource;
use Illuminate\Support\Facades\Hash;
use Illuminate\Http\Request;


class UserController extends Controller
{
// Lista con paginación y filtro simple
public function index(Request $request)
{
$perPage = $request->query('per_page', 10);
$q = $request->query('q');


$query = User::query();


if ($q) {
$query->where(function($qbuilder) use ($q) {
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
return (new UserResource($user))->response()->setStatusCode(201);
}


public function update(UpdateUserRequest $request, User $user)
{
$data = $request->validated();


if (isset($data['password'])) {
$data['password'] = Hash::make($data['password']);
}
}
}