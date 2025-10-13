<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Cuenta;
use Illuminate\Support\Facades\DB;

class CuentaController extends Controller
{


    public function index()
    {
        return response()->json(Cuenta::all());
    }

    
    public function show($id)
    {
        $account = Cuenta::findOrFail($id);
        return response()->json($account);
    }

        public function store(Request $request)
    {
        //$request->validate([
          //  'numero_cuenta' => 'required|unique:cuentas',
           // 'nombre' => 'required',
            //'monto' => 'numeric|min:0'
       // ]);

        $account = Cuenta::create($request->all());
        return response()->json($account, 201);

    }

      public function update(Request $request, $id)
    {
        $account = Cuenta::findOrFail($id);
        $account->update($request->all());
        return response()->json($account);
    }

      public function destroy($id)
    {
        Cuenta::destroy($id);
        return response()->json(['message' => 'Cuenta eliminada correctamente']);
    }



    // Depositar dinero
    public function deposit(Request $request, $id)
    {
        $request->validate(['monto' => 'required|numeric|min:1']);
        $account = Cuenta::findOrFail($id);
        $account->monto += $request->monto;
        $account->save();
        return response()->json(['message' => 'Depósito exitoso', 'nuevo_saldo' => $account->monto]);
    }


   

     public function withdraw(Request $request, $id)
    {
        $request->validate(['monto' => 'required|numeric|min:1']);
        $account = Cuenta::findOrFail($id);

        if ($account->monto < $request->monto) {
            return response()->json(['error' => 'Fondos insuficientes'], 400);
        }

        $account->monto -= $request->monto;
        $account->save();
        return response()->json(['message' => 'Retiro exitoso', 'nuevo_saldo' => $account->monto]);
    }


  public function transfer(Request $request)
{
    $request->validate([
        'cuenta_origen' => 'required|exists:cuentas,numero_cuenta',
        'cuenta_destino' => 'required|exists:cuentas,numero_cuenta|different:cuenta_origen',
        'monto' => 'required|numeric|min:1',
    ]);

    $origen = Cuenta::where('numero_cuenta', $request->cuenta_origen)->first();
    $destino = Cuenta::where('numero_cuenta', $request->cuenta_destino)->first();

    if (!($origen && $destino)) {
        return response()->json([
            'error' => 'Una o ambas cuentas no existen en el sistema.'
        ], 404);
    }

    if ($origen->monto < $request->monto) {
        return response()->json([
            'error' => 'Fondos insuficientes en la cuenta origen'
        ], 400);
    }

    $origen->monto -= $request->monto;
    $destino->monto += $request->monto;

    $origen->save();
    $destino->save();

    return response()->json([
        'message' => 'Transferencia exitosa'
    ], 200);
}


    }

  

