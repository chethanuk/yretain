# yretain
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/badge/fastapi-v.0.85.0-blue)
![GitHub](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![GitHub](https://img.shields.io/badge/license-Apache2.0-blue)

---

### Run Locally:

```bash
#Start poetry shell
poetry shell
# Run app
uvicorn --factory --host 127.0.0.1 --port 8001 --reload yretain.app:get_application
```

Deploy to EBS:
```bash
mkdir elastic_beanstalk
cd elastic_beanstalk
export PROJECT=cpp-project-x21205825
eb init -r us-east-1 -p docker $PROJECT
eb create $PROJECT --service-role LabRole --instance_profile LabInstanceProfile --timeout 100
eb deploy $PROJECT
```

```bash
docker build -t 470594810414.dkr.ecr.us-east-1.amazonaws.com/yretain:0.3 .  
docker push 470594810414.dkr.ecr.us-east-1.amazonaws.com/yretain:0.3
```

API To register User:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "vishwas1@example.com",
  "password": "vishwas1",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}'

Response: 
{"id":"d360681b-4260-4678-82b2-e7c42d8bad03","email":"vishwas1@example.com","is_active":true,"is_superuser":false,"is_verified":false}%   

```

### Documentation

You should have documentation deployed to your project GitHub pages via [Build Docs workflow](https://yretain.com/actions/workflows/docs.yml)

**NOTE!** You might need to enable GitHub pages for this project first.

To build docs manually:
```shell
make docs
```

Then open `./site/index.html` with any browser.

## License

This project is licensed under the terms of the Apache2.0 license.
