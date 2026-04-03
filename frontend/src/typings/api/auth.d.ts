declare namespace Api {
  /**
   * namespace Auth
   *
   * backend api module: "auth"
   */
  namespace Auth {
    interface RegisterCompanyRequest {
      company_name: string;
      full_name: string;
      email: string;
      password: string;
    }

    interface RegisterCompanyResponse {
      companyId: string;
      companyName: string;
      adminEmail: string;
    }

    interface LoginToken {
      token: string;
      refreshToken: string;
    }

    interface UserInfo {
      userId: string;
      userName: string;
      roles: string[];
      buttons: string[];
      tenantId?: string | null;
      companyId?: string | null;
      companyName?: string | null;
    }
  }
}
