docker-compose up -d --build
sudo docker cp hk_leaderboard-frontend-1:/app/dist .
sudo chown -R marat:marat dist
sudo usermod -a -G marat www-data
