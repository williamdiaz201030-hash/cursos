db.createUser({
  user: "coursesuser",
  pwd: "coursespass123",
  roles: [
    {
      role: "readWrite",
      db: "courses_content"
    }
  ]
});