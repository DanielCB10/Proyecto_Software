<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Tymon\JWTAuth\Facades\JWTAuth;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;

class AuthController extends Controller
{
    public function login(Request $request)
    {
        $credentials = $request->only(['email','password']);

        if (! $token = auth('api')->attempt($credentials)) {
            return response()->json(['error' => 'Credenciales inválidas'], 401);
        }

        return $this->respondWithToken($token, auth('api')->user());
    }

    public function register(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
            'password' => 'required|confirmed|min:6'
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $user = User::create([
            'name' => $request->name,
            'email'=> $request->email,
            'password'=> Hash::make($request->password),
        ]);

        $token = auth('api')->login($user);

        return $this->respondWithToken($token, $user);
    }

    // Refresh token (usa JWTAuth o auth('api'))
    public function refresh()
    {
        // Opción con guard explícito:
        // $token = auth('api')->refresh();

        // Opción con facade (recomendada para evitar warnings del IDE)
        $token = JWTAuth::refresh(JWTAuth::getToken());

        return $this->respondWithToken($token, auth('api')->user());
    }

    protected function respondWithToken($token, $user = null)
    {
        return response()->json([
            'access_token' => $token,
            'token_type'   => 'bearer',
            // Opción guard explícito:
            // 'expires_in' => auth('api')->factory()->getTTL() * 60,
            // Opción facade:
            'expires_in'   => JWTAuth::factory()->getTTL() * 60,
            'user'         => $user,
        ]);
    }

    public function logout()
    {
        auth('api')->logout();
        return response()->json(['message' => 'Sesión cerrada']);
    }

    public function me()
    {
        return response()->json(auth('api')->user());
    }
}
