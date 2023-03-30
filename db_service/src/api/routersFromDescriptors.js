'use strict';
const {addRouterMethods} = require('./routers');
const {ROUTE_DESCRIPTORS} = require('./routeDescriptors');
const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.exports = router;

for (const descriptor of ROUTE_DESCRIPTORS) {
  addRouterMethods(router, descriptor);
}
