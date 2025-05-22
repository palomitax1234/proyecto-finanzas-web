from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esta clave para seguridad

USUARIO = "directiva"
CONTRASENA = "1234"
ARCHIVO_DATOS = "datos.csv"

def inicializar_archivo():
    if not os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Tipo", "Monto", "Descripción"])

def agregar_movimiento(tipo, monto, descripcion):
    with open(ARCHIVO_DATOS, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo, monto, descripcion])

def leer_datos():
    ingresos = 0
    gastos = 0
    movimientos = []
    if not os.path.exists(ARCHIVO_DATOS):
        return ingresos, gastos, movimientos
    with open(ARCHIVO_DATOS, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            monto = float(fila["Monto"])
            movimientos.append(fila)
            if fila["Tipo"] == "Ingreso":
                ingresos += monto
            elif fila["Tipo"] == "Gasto":
                gastos += monto
    return ingresos, gastos, movimientos

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')
        if usuario == USUARIO and clave == CONTRASENA:
            session['usuario'] = usuario
            flash('Acceso concedido', 'success')
            return redirect(url_for('registro'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        monto = request.form.get('monto')
        descripcion = request.form.get('descripcion')
        try:
            monto_float = float(monto)
            if tipo not in ['Ingreso', 'Gasto']:
                flash('Tipo inválido', 'warning')
            elif monto_float <= 0:
                flash('Monto debe ser mayor que cero', 'warning')
            else:
                agregar_movimiento(tipo, monto_float, descripcion)
                flash('Movimiento registrado', 'success')
                return redirect(url_for('registro'))
        except ValueError:
            flash('Monto inválido', 'warning')
    return render_template('registro.html')

@app.route('/reporte')
def reporte():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    ingresos, gastos, movimientos = leer_datos()
    balance = ingresos - gastos
    return render_template('reporte.html', ingresos=ingresos, gastos=gastos, balance=balance, movimientos=movimientos)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    inicializar_archivo()
    app.run(debug=True)
