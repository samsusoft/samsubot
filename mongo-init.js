db = db.getSiblingDB('samsubot');
db.createUser({
  user: 'samsu',
  pwd: 'secret123',
  roles: [
    {
      role: 'readWrite',
      db: 'samsubot',
    },
  ],
});
