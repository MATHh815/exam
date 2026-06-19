/**
 * Property-based tests for user store authentication token management
 * Feature: auth-token-fix
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
global.localStorage = localStorageMock

// Mock fetch for API calls
global.fetch = vi.fn()

// Mock the auth API module
vi.mock('../api/auth', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  getProfile: vi.fn(),
  register: vi.fn()
}))

// Mock the request utility
vi.mock('../utils/request', () => ({
  default: vi.fn()
}))

// Mock the storage utility
vi.mock('../utils/storage', () => ({
  default: {
    set: vi.fn(),
    get: vi.fn(),
    remove: vi.fn()
  }
}))

describe('User Store Authentication Token Management', () => {
  let userStore
  let mockLoginApi

  beforeEach(async () => {
    // Reset all mocks
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    
    // Setup mock for login API
    mockLoginApi = vi.fn()
    
    // Import the auth module and get the mocked login function
    const authModule = await import('../api/auth')
    authModule.login.mockImplementation(mockLoginApi)
    
    // Create fresh pinia instance
    setActivePinia(createPinia())
    
    // Import and create user store
    const { useUserStore } = await import('../stores/user.js')
    userStore = useUserStore()
  })

  describe('Property 1: Login token persistence', () => {
    /**
     * **Feature: auth-token-fix, Property 1: Login token persistence**
     * For any successful login operation, the access token should be immediately stored in localStorage
     * **Validates: Requirements 1.1**
     */
    it('should immediately store access token in localStorage on successful login', async () => {
      // Generate test data
      const testCases = [
        {
          loginData: { username: 'user1', password: 'pass1' },
          responseData: {
            success: true,
            data: {
              access_token: 'token123',
              refresh_token: 'refresh123',
              user: { id: 1, username: 'user1', email: 'user1@test.com' }
            }
          }
        },
        {
          loginData: { username: 'admin', password: 'adminpass' },
          responseData: {
            success: true,
            data: {
              access_token: 'admin_token_456',
              refresh_token: 'admin_refresh_456',
              user: { id: 2, username: 'admin', email: 'admin@test.com', role: 'admin' }
            }
          }
        },
        {
          loginData: { username: 'test@example.com', password: 'complex_pass_123!' },
          responseData: {
            success: true,
            data: {
              access_token: 'jwt.token.here',
              refresh_token: 'refresh.token.here',
              user: { id: 3, username: 'test@example.com', email: 'test@example.com' }
            }
          }
        }
      ]

      for (const testCase of testCases) {
        // Reset mocks for each test case
        vi.clearAllMocks()
        localStorageMock.getItem.mockReturnValue(null)
        
        // Mock the login API response
        mockLoginApi.mockResolvedValue(testCase.responseData)

        // Perform login
        await userStore.login(testCase.loginData)

        // Verify token is immediately stored in localStorage
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'access_token', 
          testCase.responseData.data.access_token
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'refresh_token', 
          testCase.responseData.data.refresh_token
        )
        expect(localStorageMock.setItem).toHaveBeenCalledWith(
          'user', 
          JSON.stringify(testCase.responseData.data.user)
        )
      }
    })
  })

  describe('Property 2: Login state synchronization', () => {
    /**
     * **Feature: auth-token-fix, Property 2: Login state synchronization**
     * For any successful login operation, the authentication store state should be updated synchronously with the token storage
     * **Validates: Requirements 1.2**
     */
    it('should synchronously update store state with token storage on login', async () => {
      const testCases = [
        {
          access_token: 'sync_token_1',
          refresh_token: 'sync_refresh_1',
          user: { id: 1, username: 'sync_user1' }
        },
        {
          access_token: 'sync_token_2',
          refresh_token: 'sync_refresh_2',
          user: { id: 2, username: 'sync_user2', role: 'admin' }
        }
      ]

      for (const testData of testCases) {
        // Reset mocks
        vi.clearAllMocks()
        localStorageMock.getItem.mockReturnValue(null)

        const mockResponse = {
          success: true,
          data: testData
        }

        mockLoginApi.mockResolvedValue(mockResponse)

        // Perform login
        await userStore.login({ username: 'test', password: 'test' })

        // Verify store state is synchronously updated
        expect(userStore.accessToken).toBe(testData.access_token)
        expect(userStore.refreshToken).toBe(testData.refresh_token)
        expect(userStore.user).toEqual(testData.user)
        expect(userStore.isLoggedIn).toBe(true)

        // Verify localStorage calls happened
        expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', testData.access_token)
        expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', testData.refresh_token)
        expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(testData.user))
      }
    })
  })

  describe('Property 4: Store initialization restoration', () => {
    /**
     * **Feature: auth-token-fix, Property 4: Store initialization restoration**
     * For any authentication store initialization, if localStorage contains valid auth data, the store state should be restored
     * **Validates: Requirements 1.4**
     */
    it('should restore authentication state from localStorage on store initialization', () => {
      const testCases = [
        {
          storedToken: 'stored_token_1',
          storedRefreshToken: 'stored_refresh_1',
          storedUser: { id: 1, username: 'stored_user1' }
        },
        {
          storedToken: 'stored_token_2',
          storedRefreshToken: 'stored_refresh_2',
          storedUser: { id: 2, username: 'stored_user2', role: 'admin' }
        },
        {
          storedToken: 'jwt.eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9',
          storedRefreshToken: 'refresh.eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9',
          storedUser: { id: 3, username: 'jwt_user', email: 'jwt@test.com' }
        }
      ]

      for (const testData of testCases) {
        // Setup localStorage mock to return stored data
        localStorageMock.getItem.mockImplementation((key) => {
          switch (key) {
            case 'access_token':
              return testData.storedToken
            case 'refresh_token':
              return testData.storedRefreshToken
            case 'user':
              return JSON.stringify(testData.storedUser)
            default:
              return null
          }
        })

        // Create new store instance (this triggers initialization)
        setActivePinia(createPinia())
        const { useUserStore } = require('../stores/user.js')
        const store = useUserStore()

        // Verify state is restored from localStorage
        expect(store.accessToken).toBe(testData.storedToken)
        expect(store.refreshToken).toBe(testData.storedRefreshToken)
        expect(store.user).toEqual(testData.storedUser)
        expect(store.isLoggedIn).toBe(true)

        // Verify localStorage was queried
        expect(localStorageMock.getItem).toHaveBeenCalledWith('access_token')
        expect(localStorageMock.getItem).toHaveBeenCalledWith('refresh_token')
        expect(localStorageMock.getItem).toHaveBeenCalledWith('user')
      }
    })

    it('should handle partial localStorage data gracefully', () => {
      // Test case: token exists but user data is corrupted
      localStorageMock.getItem.mockImplementation((key) => {
        switch (key) {
          case 'access_token':
            return 'valid_token'
          case 'refresh_token':
            return 'valid_refresh'
          case 'user':
            return 'invalid_json_data'
          default:
            return null
        }
      })

      setActivePinia(createPinia())
      const { useUserStore } = require('../stores/user.js')
      const store = useUserStore()

      // Should restore tokens but clear corrupted user data
      expect(store.accessToken).toBe('valid_token')
      expect(store.refreshToken).toBe('valid_refresh')
      expect(store.user).toBe(null)
      expect(store.isLoggedIn).toBe(true) // Still logged in due to token
    })

    it('should clear all data when no token exists', () => {
      localStorageMock.getItem.mockReturnValue(null)

      setActivePinia(createPinia())
      const { useUserStore } = require('../stores/user.js')
      const store = useUserStore()

      expect(store.accessToken).toBe('')
      expect(store.refreshToken).toBe('')
      expect(store.user).toBe(null)
      expect(store.isLoggedIn).toBe(false)
    })
  })
})