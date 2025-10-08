<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\CuentaController;


/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});


// CRUD de cuentas
Route::get('accounts', [CuentaController::class, 'index']);           
Route::get('accounts/{id}', [CuentaController::class, 'show']);       
Route::post('accounts', [CuentaController::class, 'store']);          
Route::put('accounts/{id}', [CuentaController::class, 'update']);     
Route::delete('accounts/{id}', [CuentaController::class, 'destroy']); 



// Operaciones de cuenta
Route::post('accounts/{id}/deposit', [CuentaController::class, 'deposit']);
Route::post('accounts/{id}/withdraw', [CuentaController::class, 'withdraw']);
Route::post('accounts/transfer', [CuentaController::class, 'transfer']);
