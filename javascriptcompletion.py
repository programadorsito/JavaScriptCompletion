import sublime
import sublime_plugin
import sys
import webbrowser

"""
que no tome en cuenta cuando se trata de un ciere de etiqueta
"""
#poner en funciones a que complete los objetos

class javascriptCompletions(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		if view.scope_name(view.sel()[0].a).find("source.js.embedded.html")!=-1 or view.scope_name(0).find("source.js ")!=-1:
			linea=view.substr(sublime.Region(view.line(view.sel()[0]).a, view.sel()[0].a))
			linea=linea.strip()
			f=open(sublime.packages_path()+"\\SublimeJavascript\\js.xml")
			self.lista=f.readlines()
			f.close()
			#---quita todas las cadenas---
			while linea.rfind(")")>linea.rfind("("):
				parte=linea[linea.rfind("("):linea.rfind(")")+1]
				linea=linea.replace(parte, "")
				
			while linea.count('"')>=2:
					p=linea.find('"')
					parte=linea[p:linea.find('"', p+1)+1]
					linea=linea.replace(parte, "")
			if linea.find('"')!=-1:
				linea=linea[:linea.find('"')]

			while linea.count("'")>=2:
					p=linea.find("'")
					parte=linea[p:linea.find("'", p+1)+1]
					linea=linea.replace(parte, "")
			if linea.find("'")!=-1:
				linea=linea[:linea.find("'")]

			linea=linea.strip()
			#

			
			if linea.endswith("."):
				print("completacion de objeto")
				signatura=linea[:linea.rfind(".")]
				p=len(signatura)-1
				i=-1
				while p>=0:
					c=signatura[i]
					if not (c.isalpha() or c=='.' or c=='_' or c=='$'):break
					p-=1
					i-=1
				signatura=signatura[p+1:]
				linea=signatura+linea[linea.rfind("."):]
				palabra=linea[:-1]
				print("este es el resuzltado final de la linea", palabra)
				return self.miembros(palabra)

			elif linea.endswith(",") or linea.endswith("("):
				print("completacion de parametro")
				signatura=linea[:linea.rfind("(")]
				p=len(signatura)-1
				i=-1
				while p>=0:
					c=signatura[i]
					if not (c.isalpha() or c=='.' or c=='_' or c=='$'):break
					p-=1
					i-=1
				signatura=signatura[p+1:]
				linea=signatura+linea[linea.rfind("("):]
				print("asi quedo la linea : ", linea)
				metodo=""
				objeto=None
				pos=0
				if signatura.find(".")!=-1:
					metodo=linea[linea.find(".")+1:linea.find("(")]
					objeto=linea[:linea.find(".")]
				else:
					metodo=linea[:linea.find("(")]
				pos=linea.count(",")+1
				if objeto:
					return self.completarParametros(metodo, str(pos), objeto)
				else:
					return self.completarParametros(metodo, str(pos))
			else:
				return self.funciones()

	def miembros(self, objeto):
		lista=[]
		objeto=objeto.lower()
		if not self.objetoReconocido(objeto):return self.buscarVariable(objeto)
		activado=False
		print("antes de")
		for l in self.lista:
			if l.find("<object ")!=-1:
				miembros=self.extraerMiembros(l, ["name"])
				#print(miembros)
				if miembros["name"].lower().strip()==objeto.lower().strip():
					activado=True
					continue
			if activado and l.find("</object")!=-1:
				break
			elif activado:
				miembros=self.extraerMiembros(l, ["name", "completion", "help", "return"])
				if miembros["return"]:
					print(miembros)
					lista.append((miembros["name"]+("\t•(%s)"%miembros["return"])+miembros["help"],miembros["completion"]))
				else:
					lista.append((miembros["name"]+"\t•"+miembros["help"],miembros["completion"]))
		return lista

	def funciones(self):
		lista=self.miembros("window")
		for l in self.lista:
			if l.find("<global ")!=-1:
				miembros=self.extraerMiembros(l, ["name", "completion", "help"])
				lista.append((miembros["name"]+"\t•"+miembros["help"],miembros["completion"]))
			elif l.find("<object ")!=-1:
				miembros=self.extraerMiembros(l, ["name", "help"])
				lista.append((miembros["name"]+"\t•"+miembros["help"], miembros["name"]))
		return lista

	def objetoReconocido(self, objeto):
		objectos=[]
		for l in self.lista:
			if l.find("<object ")!=-1:
				p=l.find("name='")+6
				nombre=l[p:l.find("'", p)]
				objectos.append(nombre.strip().lower())
		return objeto in objectos

	def buscarVariable(self, objeto, nombre=False):
		print("ultima parada , ", objeto)
		view=sublime.active_window().active_view()
		lista=view.substr(sublime.Region(0, view.size())).splitlines()
		linea=view.substr(view.line(view.sel()[0].a))
		p=0
		for l in lista:
			if l==linea:break
			p+=1
		i=0
		if p!=0:i=p-1
		else:i=p
		listaInicial=[]
		contador=0
		while i>=0:
			if lista[i].endswith("}"):contador+=1
			if lista[i].endswith("{"):contador-=1
			if contador==0:listaInicial.append(lista[i])
			i-=1
		lista=listaInicial

		for l in lista:
			if l.find(objeto+"=")!=-1 or l.find(objeto+" =")!=-1:
				palabra=self.identificarTipo(l[l.rfind("=")+1:l.rfind(";")])
				if palabra:
					if nombre:
						return palabra.strip()
					else:
						return self.miembros(palabra.strip())
				else:
					sublime.status_message("jaja no hay nada")

	def identificarTipo(self, palabra):
		palabra=palabra.strip()
		objeto=""
		if palabra.find(".")!=-1:
			objeto=self.buscarVariable(palabra[:palabra.find(".")], True)
			print("asi ha quedado el objeto", objeto)
		palabra=palabra.strip()
		if palabra.startswith("require("):
			palabra=palabra[palabra.find("(")+1:palabra.find(")")]
			palabra=palabra.replace('"', "")
			palabra=palabra.replace("'", "")
		print("la palabra potencial es :", palabra)
		if palabra.find("Array(")!=-1:
			return "array"
		if palabra.find("Date(")!=-1:
			return "date"


		if palabra.endswith('"') and palabra.startswith('"') or palabra.endswith("'") and palabra.startswith("'"):
			return "string"
		elif self.objetoReconocido(palabra):
			return palabra
		elif palabra.endswith(")"):
			if palabra.find(".")==-1:
				return self.retornoMetodo(palabra[:palabra.find("(")])
			else:
				return self.retornoMetodo(palabra[palabra.find(".")+1:palabra.find("(")], objeto)

		else:
			try:
				n=float(palabra)
				return "number"
			except:
				return None

	def retornoMetodo(self, metodo, objeto=None):
		print("retorno de metodo", metodo,":", objeto)
		metodo=metodo.strip()
		if not objeto:
			for l in self.lista:
				if l.find("<global ")!=-1:
					miembros=self.extraerMiembros(l, ["name", "return"])
					if miembros["name"].strip()==metodo:
						return miembros["return"]
		else:
			objetoEncontrado=False
			for l in self.lista:
				if objetoEncontrado:
					if l.find("<member ")!=-1:
						miembros=self.extraerMiembros(l, ["name", "return"])
						if miembros["name"].strip()==metodo.lower().strip():
							print("el objeto retorna", miembros["return"])
							return miembros["return"]
					else:break

				if l.find("<object ")!=-1:
					miembros=self.extraerMiembros(l, ["name"])
					if miembros["name"].strip()==objeto.strip():
						print("el objeto se encontro")
						objetoEncontrado=True
						continue

	def completarParametros(self, metodo, posicion, objeto=None):
		lista=[]
		hayObjeto=False
		if objeto:
			hayObjeto=True
		else:
			objeto="window"

		objetoEncontrado=metodoEncontrado=False
		for l in self.lista:
			if objetoEncontrado and metodoEncontrado:
				if l.find("<param ")!=-1:
					miembros=self.extraerMiembros(l, ["name", "completion", "pos", "help"])
					if miembros["pos"].strip()==posicion.strip():
						lista.append((miembros["name"]+"\t•"+miembros["help"], miembros["completion"]))
					continue
				else:break

			if not objetoEncontrado and l.find("<object ")!=-1:
				p=l.find("name='")+6
				nombre=l[p:l.find("'", p)]
				if objeto.strip()==nombre:
					objetoEncontrado=True
					continue

			if not metodoEncontrado and l.find("<member ")!=-1:
				p=l.find("name='")+6
				nombre=l[p:l.find("'", p)]
				if metodo==nombre:
					metodoEncontrado=True
					continue

		if not hayObjeto and not lista:
			metodoEncontrado=False
			for l in self.lista:
				if metodoEncontrado:
					if l.find("<param ")!=-1:
						miembros=self.extraerMiembros(l, ["name", "completion", "pos", "help"])
						if miembros["pos"].strip()==posicion.strip():
							lista.append((miembros["name"]+"\t•"+miembros["help"], miembros["completion"]))
						continue
					else:break

				if not metodoEncontrado and l.find("<global "):
					p=l.find("name='")+6
					nombre=l[p:l.find("'", p)]
					if metodo==nombre:
						metodoEncontrado=True
						continue
		return lista

	def extraerMiembros(self, linea, lista):
		miembros={}
		for m in lista:
			m=m.strip()
			if linea.find(m+"='")==-1:
				miembros[m]=None
				continue
			p=linea.find(m+"='")+len(m)+2
			miembros[m]=linea[p:linea.find("'", p)]
		return miembros
