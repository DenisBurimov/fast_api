# Oculo FastApi.app

Place your credential file at ~/.ssh/ and modify permissions
```
chmod 400 ~/.ssh/yourcredsfile.pem
```

Enter EC2 (There is not Ubuntu but AWS Linux)
```
ssh -i ~/.ssh/api_access.pem ec2-user@ec2-3-91-223-27.compute-1.amazonaws.com
```

To see active brunch and other brunches
```
git brunch -a
```

To redeploy last changes
```
git pull
docker-compose build
docker-compose down
docker-compose up -d
```
