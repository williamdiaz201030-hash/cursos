// db.createUser({
//   user: "authuser",
//   pwd: "authpass123",
//   roles: [
//     {
//       role: "readWrite",
//       db: "auth_db"
//     }
//   ]
// });

db = db.getSiblingDB('auth_db');

db.createUser({
  user: "mongoadmin",
  pwd: "mongopass123",
  roles: [
    { role: "readWrite", db: "auth_db" }
  ]
});