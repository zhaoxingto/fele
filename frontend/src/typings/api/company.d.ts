declare namespace Api {
  namespace Company {
    interface CompanyProfile {
      tenantId: string;
      companyId: string;
      companyName: string;
      legalName?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      address?: string | null;
      remark?: string | null;
    }

    interface UpdateCompanyProfilePayload {
      companyName: string;
      legalName?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      address?: string | null;
      remark?: string | null;
    }

    interface CodeRuleConfig {
      mode: 'sequence' | 'random' | 'date_random';
      prefix?: string | null;
      digits: number;
      nextNumber: number;
    }

    interface CompanyCodeRules {
      sku: CodeRuleConfig;
      barcode: CodeRuleConfig;
    }

    interface GenerateCodePayload {
      kind: 'sku' | 'barcode';
    }

    interface GenerateCodeResponse {
      kind: 'sku' | 'barcode';
      code: string;
      nextNumber: number;
    }

    interface CustomerItem {
      id: string;
      name: string;
      code?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      address?: string | null;
      remark?: string | null;
      isActive: boolean;
      createdAt: string;
      updatedAt: string;
    }

    interface CustomerPayload {
      name: string;
      code?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      address?: string | null;
      remark?: string | null;
      isActive: boolean;
    }

    interface SupplierItem {
      id: string;
      name: string;
      code?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      address?: string | null;
      remark?: string | null;
      isActive: boolean;
      createdAt: string;
      updatedAt: string;
    }

    interface SupplierPayload {
      name: string;
      code?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      address?: string | null;
      remark?: string | null;
      isActive: boolean;
    }

    interface CategoryItem {
      id: string;
      name: string;
      code?: string | null;
      remark?: string | null;
      isActive: boolean;
      createdAt: string;
      updatedAt: string;
    }

    interface CategoryPayload {
      name: string;
      code?: string | null;
      remark?: string | null;
      isActive: boolean;
    }

    interface ProductItem {
      id: string;
      sku: string;
      barcode?: string | null;
      name: string;
      categoryId?: string | null;
      categoryName?: string | null;
      specification?: string | null;
      unit: string;
      remark?: string | null;
      isActive: boolean;
      createdAt: string;
      updatedAt: string;
    }

    interface ProductPayload {
      sku: string;
      barcode?: string | null;
      name: string;
      categoryId?: string | null;
      specification?: string | null;
      unit: string;
      remark?: string | null;
      isActive: boolean;
    }

    interface AdminTenantListItem {
      id: string;
      companyId: string;
      companyName: string;
      legalName?: string | null;
      contactName?: string | null;
      phone?: string | null;
      email?: string | null;
      schemaName: string;
      ownerName?: string | null;
      ownerEmail?: string | null;
      isActive: boolean;
      createdAt: string;
      updatedAt: string;
    }

    interface AdminTenantDetail extends AdminTenantListItem {
      address?: string | null;
      remark?: string | null;
      subscriptionPlan?: string | null;
      subscriptionStatus?: string | null;
      subscriptionExpiresAt?: string | null;
      subscriptionScope?: string | null;
    }

    interface AdminAccountItem {
      id: string;
      fullName: string;
      email: string;
      accountType: 'platform' | 'company_admin';
      tenantName?: string | null;
      tenantId?: string | null;
      tenantRole?: string | null;
      isActive: boolean;
      createdAt: string;
      updatedAt: string;
    }

    interface AdminAccountPasswordResetPayload {
      newPassword: string;
    }

    interface AdminAccountLoginHistoryItem {
      id: string;
      loginAt: string;
      loginIp?: string | null;
    }

    interface AdminSubscriptionItem {
      tenantId: string;
      companyId: string;
      companyName: string;
      subscriptionPlan?: string | null;
      subscriptionStatus?: string | null;
      subscriptionExpiresAt?: string | null;
      subscriptionScope?: string | null;
      isActive: boolean;
      updatedAt: string;
    }

    interface AdminSubscriptionPayload {
      subscriptionPlan?: string | null;
      subscriptionStatus?: string | null;
      subscriptionExpiresAt?: string | null;
      subscriptionScope?: string | null;
    }
  }
}
