<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Mail;
use App\Jobs\SendOperationEmail;

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

Route::post('test/notify-sync', function (Request $request) {
    $data = $request->input('data', []);
    $email = $request->input('email', env('MAIL_FROM_ADDRESS'));
    $subject = $request->input('subject', $data['title'] ?? 'Prueba de notificación');

    Mail::to($email)->send(new \App\Mail\OperationNotification(array_merge(['subject' => $subject], $data)));

    return response()->json(['message' => 'Email enviado (sync)'], 200);
});


Route::post('test/notify-job', function (Request $request) {
    $data = $request->input('data', []);
    $email = $request->input('email', env('MAIL_FROM_ADDRESS'));
    $subject = $request->input('subject', $data['title'] ?? 'Prueba de notificación');

    SendOperationEmail::dispatch($email, array_merge(['subject' => $subject], $data));

    return response()->json(['message' => 'Job encolado (ver worker)'], 202);
});
