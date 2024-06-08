# Wallet Wave is open-source AI-powered transaction tracker. 

[![Demo](/docs/loom_preview.png)](https://www.loom.com/share/f4a399d6827f4413bd8f2f0b65b56043)

## Getting started
To get started with Wallet Wave backend, follow these simple steps:

### 1. Clone the repository
```bash
git clone https://github.com/walletwave_backend.git
```

### 2. Add .env file 
```txt
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SECRET_KEY=
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=
EXCHANGE_RATE_API_URL=
DEBUG = 1
DJANGO_ALLOWED_HOSTS =
REDIS_URL=
LOOPS_API_KEY = 
```
Note 1: [Redis](https://redis.io/), [Supabase](https://supabase.com), [Loops](https://www.loops.so/) and [ExchangeRate](https://www.exchangerate-api.com/) are 3rd party tools, to get the keys, please create your own accounts. They are mostly free to use at some level. 

Note 2: OpenAI key is user based, so each user can have their own key, it is not on env level. 

### 3. Build docker image
```bash
docker-compose build
```

### 4. Run the project 
```bash 
docker-compose up
```

## Project Featuers 

### AI Transaction Tracker
Simple call to OpenAI API to convert natural lanugage input to structured JSON and add it to the database. 

### Reccuring Transaction Tracker
Celery & Celery Beat for tracking reccuring transaction day — automatically add them into the transaction db and also for email notificitions 2 days before transaction charge day. 

### Chat 
2 call to OpenAI to be answer on user question. 

- 1st call to validate question and identif either it is question about transactions or not. If yes — put transactions into prompt. 
- 2nd call to answer on the question. 

It also store the previous messages, they leave on the chat level in db.

## License
Distributed under the MIT License. See [LICENSE](https://github.com/diko0071/walletwave_backend/blob/main/LICENSE.txt) for more information.








