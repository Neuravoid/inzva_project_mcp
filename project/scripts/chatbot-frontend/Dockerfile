# --- AŞAMA 1: Build ---
# React uygulamasını build etmek için Node.js ortamını kullan
FROM node:20-alpine as build

# Çalışma dizinini ayarla
WORKDIR /app

# package.json ve package-lock.json dosyalarını kopyala
COPY package*.json ./

# Gerekli node modüllerini kur
RUN npm install

# Proje dosyalarının geri kalanını kopyala
COPY . .

# React uygulamasını production için build et
RUN npm run build

# --- AŞAMA 2: Serve ---
# Build edilen dosyaları sunmak için hafif bir Nginx sunucusu kullan
FROM nginx:1.25-alpine

# Build aşamasından build edilmiş dosyaları Nginx'in sunum klasörüne kopyala
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx'in React Router gibi client-side yönlendirmeleri doğru handle etmesi için
# varsayılan config dosyasını silip yenisini ekleyeceğiz.
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

# Sunucunun çalışacağı portu belirt
EXPOSE 80

# Nginx'i başlat
CMD ["nginx", "-g", "daemon off;"]
