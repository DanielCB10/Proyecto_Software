<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
{
    Schema::create('cuentas', function (Blueprint $table) {
        $table->id();
        //lave foránea hacia la tabla users
        $table->foreignId('user_id')->constrained('users')->onDelete('cascade');
        $table->string('numero_cuenta')->unique();
        $table->decimal('monto', 10, 2)->default(0);
        $table->timestamps();
    });
}


    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('cuentas');
    }
};
