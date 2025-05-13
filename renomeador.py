import os
from PySide6.QtCore import QThread, Signal


class RenomeadorThread(QThread):
    volumeTotal = Signal(int)
    contadorArquivos = Signal(int)

    def __init__(self, diretorio: str, extensoes_permitidas: list[str], usar_subpastas: bool = False):
        super().__init__()
        self.diretorio = diretorio
        self.extensoes_permitidas = [e.lower() for e in extensoes_permitidas]
        self.usar_subpastas = usar_subpastas

    def run(self):
        total = 0
        renomeados = 0

        arquivos = self._coletar_arquivos()

        self.volumeTotal.emit(len(arquivos))

        for caminho_completo in arquivos:
            pasta, nome_arquivo = os.path.split(caminho_completo)
            nome, ext = os.path.splitext(nome_arquivo)

            if ext.lower() not in self.extensoes_permitidas:
                continue

            tamanho_total = len(nome_arquivo)
            if tamanho_total > 30:
                novo_nome = self._encurtar_nome(nome, ext)
                novo_nome = self._resolver_duplicatas(pasta, novo_nome, ext)
                novo_caminho = os.path.join(pasta, novo_nome)

                try:
                    os.rename(caminho_completo, novo_caminho)
                    renomeados += 1
                    self.contadorArquivos.emit(renomeados)
                except Exception as e:
                    print(f"Erro ao renomear: {caminho_completo} -> {novo_caminho}\n{e}")

    def _coletar_arquivos(self) -> list[str]:
        arquivos = []

        if self.usar_subpastas:
            for root, _, files in os.walk(self.diretorio):
                for f in files:
                    caminho = os.path.join(root, f)
                    if os.path.isfile(caminho):
                        arquivos.append(caminho)
        else:
            for nome in os.listdir(self.diretorio):
                caminho = os.path.join(self.diretorio, nome)
                if os.path.isfile(caminho):
                    arquivos.append(caminho)

        return arquivos

    def _encurtar_nome(self, nome: str, ext: str) -> str:
        limite = 30 - len(ext)  # ext inclui o ponto, ex: ".jpg" = 4
        if limite <= 0:
            return "arquivo" + ext  # fallback se extensão for gigante
        return nome[:limite] + ext

    def _resolver_duplicatas(self, pasta: str, nome: str, ext: str) -> str:
        caminho = os.path.join(pasta, nome)
        contador = 1

        while os.path.exists(caminho):
            base_nome, _ = os.path.splitext(nome)
            sufixo = f" ({contador})"
            limite = 30 - len(ext) - len(sufixo)

            novo_nome = base_nome[:limite] + sufixo + ext
            caminho = os.path.join(pasta, novo_nome)
            contador += 1

        return os.path.basename(caminho)
