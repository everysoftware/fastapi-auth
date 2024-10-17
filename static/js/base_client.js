export class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, params = {}, method = 'GET', body = null, headers = {}, customErrorHandler = null) {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        const options = {
            method,
            headers: headers,
            credentials: 'include'
        };

        if (body) {
            if (body.constructor === Object) {
                options.body = JSON.stringify(body);
                options.headers['Content-Type'] = 'application/json';
            } else if (body.constructor === URLSearchParams) {
                options.body = body;
                options.headers['Content-Type'] = 'application/x-www-form-urlencoded';
            } else {
                options.body = body;
            }
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json();
                if (customErrorHandler) {
                    customErrorHandler(response.status, errorData);
                } else {
                    this.handleErrors(response.status, errorData);
                }
                return null;
            }
            return response;
        } catch (error) {
            console.error('Network error:', error);
            alert('A network error occurred. Please try again.');
            return null;
        }
    }

    handleErrors(status, data) {
        switch (status) {
            case 422:
                alert('Validation error: ' + (data.detail || 'Unknown error.'));
                break;
            case 404:
                alert('The requested resource was not found.');
                break;
            case 500:
                alert('Internal server error. Please try again later.');
                break;
            default:
                alert('An error occurred: ' + (data.detail || 'Unknown error.'));
        }
    }

    post(endpoint, params = {}, body = {}, headers = {}, customErrorHandler = null) {
        return this.request(endpoint, params, 'POST', body, headers, customErrorHandler);
    }

    get(endpoint, params = {}, headers = {}, customErrorHandler = null) {
        return this.request(endpoint, params, 'GET', null, headers, customErrorHandler);
    }

    put(endpoint, params = {}, body = {}, headers = {}, customErrorHandler = null) {
        return this.request(endpoint, params, 'PUT', body, headers, customErrorHandler);
    }

    patch(endpoint, params = {}, body = {}, headers = {}, customErrorHandler = null) {
        return this.request(endpoint, params, 'PATCH', body, headers, customErrorHandler);
    }

    delete(endpoint, params = {}, headers = {}, customErrorHandler = null) {
        return this.request(endpoint, params, 'DELETE', null, headers, customErrorHandler);
    }
}
