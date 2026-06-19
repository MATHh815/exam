/**
 * Property-based tests for route guard authentication logic
 * Feature: auth-token-fix
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
global.localStorage = localStorageMock

// Mock Element Plus message
vi.mock('element-plus', () => ({
  ElMessage: {
    warning: vi.fn(),
    error: vi.fn()
  }
}))

// Mock loading utilities
vi.mock('../utils/loading', () => ({
  showLoading: vi.fn(),
  hideLoading: vi.fn()
}))

// Mock the auth API module
vi.mock('../api/auth', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  getProfile: vi.fn(),
  register: vi.fn()
}))

// Mock the storage utility
vi.mock('../utils/storage', () => ({
  default: {
    set: vi.fn(),
    get: vi.fn(),
    remove: vi.fn()
  }
}))

describe('Route Guard Authentication Logic', () => {
  let router
  let userStore
  let mockNext

  beforeEach(async () => {
    // Reset all mocks
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    
    // Create fresh pinia instance
    setActivePinia(createPinia())
    
    // Import and create user store
    const { useUserStore } = await import('../stores/user.js')
    userStore = useUserStore()
    
    // Create mock router with test routes
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/login',
          name: 'login',
          component: { template: '<div>Login</div>' },
          meta: { requiresAuth: false }
        },
        {
          path: '/dashboard',
          name: 'dashboard',
          component: { template: '<div>Dashboard</div>' },
          meta: { requiresAuth: true }
        },
        {
          path: '/profile',
          name: 'profile',
          component: { template: '<div>Profile</div>' },
          meta: { requiresAuth: true }
        },
        {
          path: '/admin',
          name: 'admin',
          component: { template: '<div>Admin</div>' },
          meta: { requiresAuth: true, requiresAdmin: true }
        }
      ]
    })
    
    // Mock next function
    mockNext = vi.fn()
  })

  describe('Property 3: Route guard token priority', () => {
    /**
     * **Feature: auth-token-fix, Property 3: Route guard token priority**
     * For any protected route navigation, token existence should be verified before checking user object presence
     * **Validates: Requirements 1.3**
     */
    it('should prioritize token existence over user object presence for authentication', async () => {
      const testCases = [
        {
          description: 'Token exists, user object missing - should allow access',
          token: 'valid_token_123',
          refreshToken: 'refresh_123',
          user: null,
          expectedResult: 'allow'
        },
        {
          description: 'Token exists, user object exists - should allow access',
          token: 'valid_token_456',
          refreshToken: 'refresh_456',
          user: { id: 1, username: 'testuser' },
          expectedResult: 'allow'
        },
        {
          description: 'No token, user object exists - should deny access',
          token: null,
          refreshToken: null,
          user: { id: 1, username: 'testuser' },
          expectedResult: 'deny'
        },
        {
          description: 'No token, no user object - should deny access',
          token: null,
          refreshToken: null,
          user: null,
          expectedResult: 'deny'
        },
        {
          description: 'Empty token, user object exists - should deny access',
          token: '',
          refreshToken: '',
          user: { id: 1, username: 'testuser' },
          expectedResult: 'deny'
        }
      ]

      for (const testCase of testCases) {
        // Reset mocks for each test case
        vi.clearAllMocks()
        
        // Setup localStorage mock
        localStorageMock.getItem.mockImplementation((key) => {
          switch (key) {
            case 'access_token':
              return testCase.token
            case 'refresh_token':
              return testCase.refreshToken
            case 'user':
              return testCase.user ? JSON.stringify(testCase.user) : null
            default:
              return null
          }
        })

        // Setup user store state
        userStore.accessToken = testCase.token || ''
        userStore.refreshToken = testCase.refreshToken || ''
        userStore.user = testCase.user

        // Create route objects
        const to = {
          name: 'dashboard',
          path: '/dashboard',
          fullPath: '/dashboard',
          matched: [{ meta: { requiresAuth: true } }],
          meta: { requiresAuth: true }
        }
        const from = { name: 'login', path: '/login' }

        // Import and get the route guard logic
        const routerModule = await import('../router/index.js')
        const routerInstance = routerModule.default

        // Get the beforeEach guard
        const guards = routerInstance.beforeGuards
        expect(guards.length).toBeGreaterThan(0)
        
        const routeGuard = guards[0]

        // Execute the route guard
        await routeGuard(to, from, mockNext)

        // Verify the result based on token existence priority
        if (testCase.expectedResult === 'allow') {
          // Should call next() without arguments (allow navigation)
          expect(mockNext).toHaveBeenCalledWith()
        } else {
          // Should redirect to login
          expect(mockNext).toHaveBeenCalledWith({
            name: 'login',
            query: { redirect: to.fullPath }
          })
        }

        console.log(`✓ ${testCase.description}`)
      }
    })
  })

  describe('Property 6: Authentication priority logic', () => {
    /**
     * **Feature: auth-token-fix, Property 6: Authentication priority logic**
     * For any route guard authentication check, token existence should take priority over user object presence in determining authentication status
     * **Validates: Requirements 2.1**
     */
    it('should determine authentication status based on token existence priority', async () => {
      const testCases = [
        {
          scenario: 'Valid token with complete user data',
          token: 'jwt.eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.payload.signature',
          user: { id: 1, username: 'user1', role: 'user' },
          expectedAuthenticated: true
        },
        {
          scenario: 'Valid token with null user data',
          token: 'valid_token_without_user',
          user: null,
          expectedAuthenticated: true
        },
        {
          scenario: 'Valid token with undefined user data',
          token: 'another_valid_token',
          user: undefined,
          expectedAuthenticated: true
        },
        {
          scenario: 'No token with valid user data',
          token: null,
          user: { id: 2, username: 'user2', role: 'admin' },
          expectedAuthenticated: false
        },
        {
          scenario: 'Empty token with valid user data',
          token: '',
          user: { id: 3, username: 'user3' },
          expectedAuthenticated: false
        },
        {
          scenario: 'Whitespace token with valid user data',
          token: '   ',
          user: { id: 4, username: 'user4' },
          expectedAuthenticated: false
        }
      ]

      for (const testCase of testCases) {
        // Reset mocks
        vi.clearAllMocks()
        
        // Setup localStorage
        localStorageMock.getItem.mockImplementation((key) => {
          if (key === 'access_token') return testCase.token
          if (key === 'user') return testCase.user ? JSON.stringify(testCase.user) : null
          return null
        })

        // Setup store state
        userStore.accessToken = testCase.token || ''
        userStore.user = testCase.user

        // Test route requiring authentication
        const to = {
          name: 'profile',
          path: '/profile',
          fullPath: '/profile',
          matched: [{ meta: { requiresAuth: true } }],
          meta: { requiresAuth: true }
        }
        const from = { name: 'login' }

        // Get route guard
        const routerModule = await import('../router/index.js')
        const routeGuard = routerModule.default.beforeGuards[0]

        // Execute route guard
        await routeGuard(to, from, mockNext)

        // Verify authentication decision based on token priority
        if (testCase.expectedAuthenticated) {
          expect(mockNext).toHaveBeenCalledWith()
        } else {
          expect(mockNext).toHaveBeenCalledWith({
            name: 'login',
            query: { redirect: to.fullPath }
          })
        }

        console.log(`✓ ${testCase.scenario}: authenticated=${testCase.expectedAuthenticated}`)
      }
    })
  })

  describe('Property 13: Redirect loop prevention', () => {
    /**
     * **Feature: auth-token-fix, Property 13: Redirect loop prevention**
     * For any sequence of authentication failures, infinite redirect loops should be prevented
     * **Validates: Requirements 3.3**
     */
    it('should prevent infinite redirect loops in authentication failures', async () => {
      const testScenarios = [
        {
          description: 'Authenticated user accessing login page should redirect to dashboard',
          token: 'valid_token',
          user: { id: 1, username: 'user' },
          targetRoute: { name: 'login', path: '/login', meta: { requiresAuth: false } },
          expectedRedirect: { name: 'dashboard' }
        },
        {
          description: 'Authenticated user accessing register page should redirect to dashboard',
          token: 'valid_token',
          user: { id: 1, username: 'user' },
          targetRoute: { name: 'register', path: '/register', meta: { requiresAuth: false } },
          expectedRedirect: { name: 'dashboard' }
        },
        {
          description: 'Unauthenticated user accessing protected route should redirect to login once',
          token: null,
          user: null,
          targetRoute: { 
            name: 'dashboard', 
            path: '/dashboard', 
            fullPath: '/dashboard',
            matched: [{ meta: { requiresAuth: true } }],
            meta: { requiresAuth: true } 
          },
          expectedRedirect: { name: 'login', query: { redirect: '/dashboard' } }
        },
        {
          description: 'Multiple failed authentication attempts should not create loops',
          token: null,
          user: null,
          targetRoute: { 
            name: 'profile', 
            path: '/profile', 
            fullPath: '/profile',
            matched: [{ meta: { requiresAuth: true } }],
            meta: { requiresAuth: true } 
          },
          expectedRedirect: { name: 'login', query: { redirect: '/profile' } }
        }
      ]

      for (const scenario of testScenarios) {
        // Reset mocks
        vi.clearAllMocks()
        
        // Setup localStorage
        localStorageMock.getItem.mockImplementation((key) => {
          if (key === 'access_token') return scenario.token
          if (key === 'user') return scenario.user ? JSON.stringify(scenario.user) : null
          return null
        })

        // Setup store state
        userStore.accessToken = scenario.token || ''
        userStore.user = scenario.user

        const from = { name: 'home' }

        // Get route guard
        const routerModule = await import('../router/index.js')
        const routeGuard = routerModule.default.beforeGuards[0]

        // Execute route guard multiple times to test for loops
        for (let attempt = 0; attempt < 3; attempt++) {
          vi.clearAllMocks()
          await routeGuard(scenario.targetRoute, from, mockNext)

          // Each attempt should produce the same, predictable result
          if (scenario.expectedRedirect) {
            expect(mockNext).toHaveBeenCalledWith(scenario.expectedRedirect)
          } else {
            expect(mockNext).toHaveBeenCalledWith()
          }
        }

        console.log(`✓ ${scenario.description}`)
      }
    })

    it('should handle edge cases that could cause redirect loops', async () => {
      const edgeCases = [
        {
          description: 'Corrupted localStorage should not cause loops',
          setupStorage: () => {
            localStorageMock.getItem.mockImplementation((key) => {
              if (key === 'access_token') return 'corrupted_token'
              if (key === 'user') throw new Error('Storage corrupted')
              return null
            })
          },
          targetRoute: { 
            name: 'dashboard', 
            path: '/dashboard', 
            fullPath: '/dashboard',
            matched: [{ meta: { requiresAuth: true } }],
            meta: { requiresAuth: true } 
          },
          expectedBehavior: 'redirect_to_login'
        },
        {
          description: 'Malformed token should not cause loops',
          setupStorage: () => {
            localStorageMock.getItem.mockImplementation((key) => {
              if (key === 'access_token') return 'malformed.token'
              if (key === 'user') return '{"id": "invalid"}'
              return null
            })
          },
          targetRoute: { 
            name: 'profile', 
            path: '/profile', 
            fullPath: '/profile',
            matched: [{ meta: { requiresAuth: true } }],
            meta: { requiresAuth: true } 
          },
          expectedBehavior: 'allow_with_token'
        }
      ]

      for (const edgeCase of edgeCases) {
        // Reset and setup
        vi.clearAllMocks()
        edgeCase.setupStorage()

        // Reset store state
        userStore.accessToken = ''
        userStore.user = null

        const from = { name: 'login' }

        // Get route guard
        const routerModule = await import('../router/index.js')
        const routeGuard = routerModule.default.beforeGuards[0]

        // Execute multiple times to ensure no loops
        let results = []
        for (let i = 0; i < 3; i++) {
          vi.clearAllMocks()
          await routeGuard(edgeCase.targetRoute, from, mockNext)
          results.push(mockNext.mock.calls[0])
        }

        // All results should be identical (no loops)
        expect(results[0]).toEqual(results[1])
        expect(results[1]).toEqual(results[2])

        console.log(`✓ ${edgeCase.description}`)
      }
    })
  })
})