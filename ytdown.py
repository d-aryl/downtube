import os
import subprocess
import customtkinter as ctk
from tkinter import messagebox
import threading

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("YouTube Downloader")
        self.geometry("550x400")
        self.resizable(False, False)
        
        # Configurar tema
        ctk.set_appearance_mode("System")  # "Dark", "Light" o "System"
        ctk.set_default_color_theme("blue")  # Temas: blue, green, dark-blue
        
        # Variables
        self.url_var = ctk.StringVar()
        self.format_var = ctk.StringVar(value="mp3")
        self.quality_var = ctk.StringVar(value="highest")
        self.progress_var = ctk.StringVar(value="Esperando descarga...")
        self.downloading = False
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Descargar Videos de YouTube",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Campo para URL
        url_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        url_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(url_frame, text="URL de YouTube:").pack(side="left")
        url_entry = ctk.CTkEntry(
            url_frame, 
            textvariable=self.url_var, 
            width=400,
            placeholder_text="Pega la URL del video aquí..."
        )
        url_entry.pack(side="left", padx=10, expand=True, fill="x")
        
        # Opciones de formato y calidad
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 20))
        
        # Formato
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(side="left", padx=10, expand=True)
        ctk.CTkLabel(format_frame, text="Formato:").pack(anchor="w")
        format_combo = ctk.CTkComboBox(
            format_frame,
            variable=self.format_var,
            values=["mp3", "mp4"],
            state="readonly"
        )
        format_combo.pack(anchor="w")
        
        # Calidad
        quality_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        quality_frame.pack(side="left", padx=10, expand=True)
        ctk.CTkLabel(quality_frame, text="Calidad:").pack(anchor="w")
        quality_combo = ctk.CTkComboBox(
            quality_frame,
            variable=self.quality_var,
            values=["highest", "720p", "480p", "360p"],
            state="readonly"
        )
        quality_combo.pack(anchor="w")
        
        # Botón de descarga
        download_btn = ctk.CTkButton(
            main_frame,
            text="Descargar",
            command=self.start_download,
            corner_radius=8,
            fg_color="#FF0000",  # Color de YouTube
            hover_color="#CC0000"
        )
        download_btn.pack(pady=(0, 20))
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            orientation="horizontal",
            width=450,
            height=15,
            progress_color="#FF0000"
        )
        self.progress_bar.set(0)
        self.progress_bar.pack()
        
        # Etiqueta de estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            textvariable=self.progress_var,
            text_color="gray70"
        )
        self.status_label.pack(pady=(10, 0))
        
        # Configurar evento para pegar desde portapapeles
        self.bind("<Control-v>", lambda e: url_entry.event_generate('<<Paste>>'))
        
    def start_download(self):
        if self.downloading:
            messagebox.showwarning("Advertencia", "Ya hay una descarga en progreso.")
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL de YouTube.")
            return
            
        # Crear carpeta de descargas si no existe
        download_dir = os.path.join(os.getcwd(), "YouTube_Downloads")
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            
        # Iniciar descarga en un hilo separado
        self.downloading = True
        self.progress_var.set("Preparando descarga...")
        self.progress_bar.set(0)
        
        thread = threading.Thread(target=self.download_video, args=(url, download_dir), daemon=True)
        thread.start()
        
    def download_video(self, url, download_dir):
        try:
            format_type = self.format_var.get()
            quality = self.quality_var.get()
            
            # Construir comando yt-dlp según las opciones seleccionadas
            if format_type == "mp3":
                cmd = [
                    'yt-dlp.exe',
                    '-x',  # Extraer audio
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',  # Mejor calidad
                    '--output', os.path.join(download_dir, '%(title)s.%(ext)s'),
                    '--newline',  # Para poder leer el progreso
                    '--no-mtime',  # No modificar fecha del archivo
                    url
                ]
            else:
                if quality == "highest":
                    cmd = [
                        'yt-dlp.exe',
                        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        '--output', os.path.join(download_dir, '%(title)s.%(ext)s'),
                        '--newline',
                        '--no-mtime',
                        url
                    ]
                else:
                    cmd = [
                        'yt-dlp.exe',
                        '-f', f'bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        '--output', os.path.join(download_dir, '%(title)s.%(ext)s'),
                        '--newline',
                        '--no-mtime',
                        url
                    ]
            
            # Ejecutar yt-dlp y capturar la salida
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, bufsize=1)
            
            # Procesar la salida para mostrar el progreso
            for line in process.stdout:
                if "[download]" in line and "%" in line:
                    # Extraer el porcentaje de progreso
                    try:
                        percent = float(line.split("%")[0].split()[-1]) / 100
                        self.after(0, self.update_progress, percent, line.strip())
                    except:
                        pass
                elif "ERROR" in line:
                    self.after(0, self.show_error, line.strip())
                    break
            
            process.wait()
            
            if process.returncode == 0:
                self.after(0, self.download_complete, download_dir)
            else:
                self.after(0, self.show_error, "Error en la descarga. Verifica la URL e intenta nuevamente.")
                
        except Exception as e:
            self.after(0, self.show_error, f"Error inesperado: {str(e)}")
        finally:
            self.downloading = False
            
    def update_progress(self, percent, message):
        self.progress_bar.set(percent)
        self.progress_var.set(message)
        
    def download_complete(self, download_dir):
        self.progress_var.set("¡Descarga completada!")
        self.progress_bar.set(1)
        messagebox.showinfo("Éxito", "La descarga se ha completado correctamente.")
        os.startfile(download_dir)
        
    def show_error(self, message):
        self.downloading = False
        self.progress_var.set("Error en la descarga")
        self.progress_bar.set(0)
        messagebox.showerror("Error", message)


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
