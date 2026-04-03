import { request } from '../request';

export function fetchCompanyProfile() {
  return request<Api.Company.CompanyProfile>({ url: '/company/profile' });
}

export function updateCompanyProfile(payload: Api.Company.UpdateCompanyProfilePayload) {
  return request<Api.Company.CompanyProfile>({
    url: '/company/profile',
    method: 'put',
    data: payload
  });
}

export function fetchCompanyCodeRules() {
  return request<Api.Company.CompanyCodeRules>({ url: '/company/code-rules' });
}

export function updateCompanyCodeRules(payload: Api.Company.CompanyCodeRules) {
  return request<Api.Company.CompanyCodeRules>({
    url: '/company/code-rules',
    method: 'put',
    data: payload
  });
}

export function generateCompanyCode(payload: Api.Company.GenerateCodePayload) {
  return request<Api.Company.GenerateCodeResponse>({
    url: '/company/code-rules/generate',
    method: 'post',
    data: payload
  });
}

export function fetchCustomers() {
  return request<Api.Company.CustomerItem[]>({ url: '/company/customers' });
}

export function createCustomer(payload: Api.Company.CustomerPayload) {
  return request<Api.Company.CustomerItem>({
    url: '/company/customers',
    method: 'post',
    data: payload
  });
}

export function updateCustomer(id: string, payload: Api.Company.CustomerPayload) {
  return request<Api.Company.CustomerItem>({
    url: `/company/customers/${id}`,
    method: 'put',
    data: payload
  });
}

export function fetchSuppliers() {
  return request<Api.Company.SupplierItem[]>({ url: '/company/suppliers' });
}

export function createSupplier(payload: Api.Company.SupplierPayload) {
  return request<Api.Company.SupplierItem>({
    url: '/company/suppliers',
    method: 'post',
    data: payload
  });
}

export function updateSupplier(id: string, payload: Api.Company.SupplierPayload) {
  return request<Api.Company.SupplierItem>({
    url: `/company/suppliers/${id}`,
    method: 'put',
    data: payload
  });
}

export function fetchCategories() {
  return request<Api.Company.CategoryItem[]>({ url: '/company/categories' });
}

export function createCategory(payload: Api.Company.CategoryPayload) {
  return request<Api.Company.CategoryItem>({
    url: '/company/categories',
    method: 'post',
    data: payload
  });
}

export function updateCategory(id: string, payload: Api.Company.CategoryPayload) {
  return request<Api.Company.CategoryItem>({
    url: `/company/categories/${id}`,
    method: 'put',
    data: payload
  });
}

export function fetchProducts() {
  return request<Api.Company.ProductItem[]>({ url: '/company/products' });
}

export function createProduct(payload: Api.Company.ProductPayload) {
  return request<Api.Company.ProductItem>({
    url: '/company/products',
    method: 'post',
    data: payload
  });
}

export function updateProduct(id: string, payload: Api.Company.ProductPayload) {
  return request<Api.Company.ProductItem>({
    url: `/company/products/${id}`,
    method: 'put',
    data: payload
  });
}

export function fetchAdminTenants() {
  return request<Api.Company.AdminTenantListItem[]>({ url: '/company/admin/tenants' });
}

export function fetchAdminTenantDetail(id: string) {
  return request<Api.Company.AdminTenantDetail>({ url: `/company/admin/tenants/${id}` });
}

export function updateAdminTenantStatus(id: string, isActive: boolean) {
  return request<Api.Company.AdminTenantListItem>({
    url: `/company/admin/tenants/${id}/status`,
    method: 'put',
    data: { isActive }
  });
}

export function fetchAdminAccounts() {
  return request<Api.Company.AdminAccountItem[]>({ url: '/company/admin/accounts' });
}

export function updateAdminAccountStatus(id: string, isActive: boolean) {
  return request<Api.Company.AdminAccountItem>({
    url: `/company/admin/accounts/${id}/status`,
    method: 'put',
    data: { isActive }
  });
}

export function resetAdminAccountPassword(id: string, payload: Api.Company.AdminAccountPasswordResetPayload) {
  return request<{ message: string }>({
    url: `/company/admin/accounts/${id}/reset-password`,
    method: 'put',
    data: payload
  });
}

export function fetchAdminAccountLoginHistory(id: string) {
  return request<Api.Company.AdminAccountLoginHistoryItem[]>({
    url: `/company/admin/accounts/${id}/login-history`
  });
}

export function fetchAdminSubscriptions() {
  return request<Api.Company.AdminSubscriptionItem[]>({ url: '/company/admin/subscriptions' });
}

export function updateAdminSubscription(id: string, payload: Api.Company.AdminSubscriptionPayload) {
  return request<Api.Company.AdminSubscriptionItem>({
    url: `/company/admin/subscriptions/${id}`,
    method: 'put',
    data: payload
  });
}
