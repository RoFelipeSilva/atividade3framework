from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from flask_login import (current_user, LoginManager,
                             login_user, logout_user,
                             login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:9577@localhost:3306/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = 'apppegpag'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column('id_Usuario', db.Integer, primary_key=True)
    nome = db.Column('Us_Nome', db.String(100))
    email = db.Column('Us_Email', db.String(100))
    cpf = db.Column('Us_CPF', db.Integer)
    endereco = db.Column('Us_End', db.String(150))
    senha = db.Column('Us_Senha', db.String(10))

    def __init__(self, nome, email, cpf, endereco, senha):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.endereco = endereco
        self.senha = senha
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('id_categoria', db.Integer, primary_key=True)
    descricao = db.Column('cat_descricao', db.String(45))
    
    def __init__ (self, descricao):
        self.descricao = descricao

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('id_anuncio', db.Integer, primary_key=True)
    titulo = db.Column('anu_titulo', db.String(35))
    descricao = db.Column('anu_descricao', db.String(250))
    valor = db.Column('anu_valor', db.Float)
    qtde = db.Column('anu_qtde', db.Integer)
    oferta = db.Column('anu_oferta', db.String(3))
    categoria_id = db.Column('id_categoria',db.Integer, db.ForeignKey("categoria.id_categoria"))
    usuario_id = db.Column('id_Usuario',db.Integer, db.ForeignKey("usuarios.id_Usuario"))

    def __init__(self, titulo, descricao, valor, qtde, oferta, categoria_id, usuario_id):
        self.titulo = titulo
        self.descricao = descricao
        self.valor = valor
        self.qtde = qtde
        self.oferta = oferta
        self.categoria_id = categoria_id
        self.usuario_id = usuario_id

class Favorito(db.Model):
    __tablename__ = "favorito"
    id = db.Column('id', db.Integer, primary_key=True)
    anuncio_id = db.Column('anuncio_id',db.Integer)
    usuario_id = db.Column('usuario_id',db.Integer)

    def __init__(self, anuncio_id, usuario_id):
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

class Pergunta(db.Model):
    __tablename__= "pergunta"
    id = db.Column('id_pergunta', db.Integer, primary_key=True)
    pergunta = db.Column('Per_Pergunta', db.String(350))
    resposta = db.Column('Per_Resposta', db.String(350))
    anuncio_id = db.Column('id_anuncio',db.Integer, db.ForeignKey("anuncio.id_anuncio"))
    usuario_id = db.Column('id_Usuario',db.Integer, db.ForeignKey("usuarios.id_Usuario"))

    def __init__(self, pergunta, resposta, id_anuncio, id_usuario):
        self.pergunta = pergunta
        self.resposta = resposta
        self.anuncio_id = id_anuncio
        self.usuario_id = id_usuario

class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column('id', db.Integer, primary_key=True)
    qtde = db.Column('qtde', db.Integer)
    valor = db.Column('valor', db.Float)
    total = db.Column('total', db.Float)
    anuncio_id = db.Column('anuncio_id',db.Integer)
    usuario_id = db.Column('usuario_id',db.Integer)

    def __init__(self, qtde, valor, total, anuncio_id, usuario_id):
        self.qtde = qtde
        self.valor = valor
        self.total = total
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pagnaoencontrada.html', titulo = "Página não encontrada")

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = request.form.get('passwd')

        user = Usuario.query.filter_by(email=email, senha=passwd).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/")
def index():
    return render_template("index.html")

# - - - - - - - U S U Á R I O - - - - - - -

@app.route("/usuario")
@login_required
def usuario():
    return render_template('usuario.html', usuarios = Usuario.query.all(), 
    titulo="Cadastro de Usuario")

@app.route("/usuario/meuperfil")
def meuperfil():
    return render_template('meuperfil.html', favoritos = Favorito.query.all(),
    título="Meu perfil ")

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    usuario = Usuario(request.form.get('nome'), request.form.get('email'), 
    request.form.get('cpf'), request.form.get('endereco'), request.form.get('senha'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET','POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.cpf = request.form.get('cpf')
        usuario.endereco = request.form.get('endereco')
        usuario.senha = request.form.get('senha')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('perfil.html', usuario = usuario, 
    anuncios = Anuncio.query.all(),titulo="Alterar")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/perfil")
def perfil():
    return render_template('perfil.html', anuncios = Anuncio.query.all())

# - - - - - - A N Ú N C I O S - - - - - - 

@app.route("/anuncio")
def anuncio():
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), 
    categorias = Categoria.query.all(), titulo="Anuncio")

@app.route("/anuncio/comprar")
@login_required
def comprar():
    return render_template('comprar.html', anuncios = Anuncio.query.all(), 
    categorias = Categoria.query.all(), titulo="Anuncio")

@app.route("/anuncio/vender")
@login_required
def vender():
    return render_template('vender.html', anuncios = Anuncio.query.all(), 
    categorias = Categoria.query.all(), titulo="Anuncio")

@app.route("/anuncio/cadanuncio", methods=['POST'])
def cadanuncio():
    anuncio = Anuncio(request.form.get('titulo'), request.form.get('descricao'),
    request.form.get('valor'),request.form.get('qtde'),request.form.get('oferta'),
    request.form.get('categoria_id'), request.form.get('usuario_id'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('vender'))

@app.route("/anuncio/detalhar/<int:id>")
def buscaranuncio(id):
    anuncio = Anuncio.query.get(id)
    return anuncio.titulo

@app.route("/anuncio/editar/<int:id>", methods=['GET','POST'])
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    if request.method == 'POST':
        anuncio.titulo = request.form.get('titulo')
        anuncio.descricao = request.form.get('descricao')
        anuncio.valor = request.form.get('valor')
        anuncio.qtde = request.form.get('qtde')
        anuncio.oferta = request.form.get('oferta')
        anuncio.categoria = request.form.get('categoria_id')
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for('vender'))

    return render_template('editanuncio.html', anuncio = anuncio, titulo="Alterar",
    categorias = Categoria.query.all())

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('vender'))
    
# - - - - - - - - A N Ú N C I O S   P E R G U N T A S - - - - - - - - -

@app.route("/anuncio/perguntar")
def perguntar():
    return render_template('perguntar.html', perguntas = Pergunta.query.all(), 
    titulo="Pergunta", anuncios = Anuncio.query.all())

@app.route("/anuncio/cadpergunta", methods=['POST'])
def cadpergunta():
    pergunta = Pergunta(request.form.get('pergunta'), request.form.get('resposta'),
    request.form.get('anuncio_id'),request.form.get('usuario_id'))
    perguntas = Pergunta.query.all()
    db.session.add(pergunta)
    db.session.commit()
    return redirect(url_for('perguntar'))

@app.route("/anuncio/cadpergunta/<int:id>", methods=['GET','POST'])
def editarpergunta(id):
    pergunta = Pergunta.query.get(id)
    if request.method == 'POST':
        pergunta.pergunta = request.form.get('pergunta')
        pergunta.resposta = request.form.get('resposta')
        pergunta.anuncio_id = request.form.get('anuncio_id')
        pergunta.usuario_id = request.form.get('usuario_id')
        db.session.add(pergunta)
        db.session.commit()
        return redirect(url_for('perguntar'))

    return render_template('editpergunta.html', pergunta = pergunta, titulo="Responder")

@app.route("/anuncio/deletarpergunta/<int:id>")
def deletarpergunta(id):
    pergunta = Pergunta.query.get(id)
    db.session.delete(pergunta)
    db.session.commit()
    return redirect(url_for('perguntar'))

#- - - - - - - - F A V O R I T O S - - - - - - - - -

@app.route("/anuncio/favoritos")
def favoritos():
    return render_template('favoritos.html', favoritos = Favorito.query.all(),
    anuncios = Anuncio.query.all())
    

@app.route("/anuncio/cadfavorito", methods=['GET','POST'])
def cadfavorito():
    favorito = Favorito(request.form.get('anuncio_id'),request.form.get('usuario_id'))
    favoritos = Favorito.query.all()
    db.session.add(favorito)
    db.session.commit()
    return redirect(url_for('favoritos'))

@app.route("/anuncio/cadfavorito/<int:id>", methods=['GET','POST'])
def editarfavorito(id):
    favorito = Favorito.query.get(id)
    favoritos = Favorito.query.all()
    if request.method == 'POST':
        favorito.anuncio_id = request.form.get('anuncio_id')
        favorito.usuario_id = request.form.get('usuario_id')
        db.session.add(favorito)
        db.session.commit()
        return redirect(url_for('meusfavoritos'))

    return render_template('editfavorito.html', favorito = favorito, 
    anuncios = Anuncio.query.all(), titulo="Editar")

@app.route("/anuncio/deletarfavorito/<int:id>")
def deletarfavorito(id):
    favorito = Favorito.query.get(id)
    db.session.delete(favorito)
    db.session.commit()
    return redirect(url_for('meusfavoritos'))


# - - - - - - - CATEGORIAS - - - - - - -  

@app.route("/config")
@login_required
def config():
    return render_template('config.html', titulo="Configurações")

@app.route("/config/categorias")
def categorias():
    return render_template('categorias.html', categorias = Categoria.query.all(), 
    titulo='Categoria')

@app.route("/config/cadcategorias", methods=['POST'])
def cadcategorias():
    categoria = Categoria(request.form.get('descricao'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categorias'))

@app.route("/config/detalhar/<int:id>")
def buscarcategoria(id):
    categoria = Categoria.query.get(id)
    return categoria.descricao

@app.route("/config/editar/<int:id>", methods=['GET','POST'])
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categoria.descricao = request.form.get('descricao')
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for('categorias'))

    return render_template('editcategoria.html', categoria = categoria, titulo="Categorias")

@app.route("/config/deletar/<int:id>")
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categorias'))

# - - - - - - C O M P R A S - - - - - - - - - -

@app.route("/compra")
@login_required
def compra():
    return render_template('compra.html', compras = Compra.query.all(), 
    titulo="Compras", anuncios = Anuncio.query.all())

@app.route("/compra/minhascompras")
@login_required
def minhascompras():
    return render_template('minhascompras.html', compras = Compra.query.all(), 
    titulo="Minhas Compras")

@app.route("/compra/criar", methods=['POST'])
def criarcompra():
    compra = Compra(request.form.get('qtde'), request.form.get('valor'), 
    request.form.get('total'), request.form.get('anuncio_id'), request.form.get('usuario_id'))
    db.session.add(compra)
    db.session.commit()
    return redirect(url_for('compra'))

@app.route("/compra/editar/<int:id>", methods=['GET','POST'])
def editarcompra(id):
    compra = Compra.query.get(id)
    if request.method == 'POST':
        compra.qtde = request.form.get('qtde')
        compra.valor = request.form.get('valor')
        compra.total = request.form.get('total')
        compra.anuncio_id = request.form.get('anuncio_id')
        compra.usuario_id = request.form.get('usuario_id')
        db.session.add(compra)
        db.session.commit()
        return redirect(url_for('editcompra'))

    return render_template('editcompra.html', compra = compra, titulo="Compra")

@app.route("/compra/deletar/<int:id>")
def deletarcompra(id):
    compra = Compra.query.get(id)
    db.session.delete(compra)
    db.session.commit()
    return redirect(url_for('minhascompras'))

 


# - - - - - - R E L A T Ó R I O S - - - - - - -

@app.route("/relatorios")
def relatorios():
    return render_template('relatorios.html')

@app.route("/relatorios/vendas")
def relVendas():
    return render_template('relvendas.html', anuncios = Anuncio.query.all(),
    titulo="Relatório de vendas")

@app.route("/relatorios/compras")
def relCompras():
    return render_template('relcompras.html', anuncios = Anuncio.query.all(),
    titulo="Relatório de compras")

@app.route("/cad/faleconosco")
def faleconosco():
    return render_template('faleconosco.html', titulo="Fale Conosco")

@app.route("/cad/cadmsg", methods=['POST'])
def cadmsg():
    return request.form

# - - - - - - - - O F E R T A S - - - - - - - - - 

@app.route("/ofertas")
def ofertas():
    return render_template('ofertas.html', anuncios = Anuncio.query.all(),
    titulo="Ofertas e Promoções")

@app.route("/sucesso")
def sucesso():
    return render_template('sucesso.html')

@app.route("/meusfavoritos")
def meusfavoritos():
    return render_template('meusfavoritos.html', favoritos = Favorito.query.all(),
    anuncios = Anuncio.query.all())

@app.route("/quemsomos")
def quemsomos():
    return render_template('quemsomos.html', titulo="Quem somos")

if __name__ == 'pegpag.py':
    db.create_all()

app.run(debug=True)