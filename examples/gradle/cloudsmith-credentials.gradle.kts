// Cloudsmith Credential Provider for Gradle
// Add this to your build.gradle or build.gradle.kts

import java.io.ByteArrayOutputStream

/**
 * Get Cloudsmith authentication token using the Cloudsmith CLI.
 * 
 * This function calls `cloudsmith tokens get` to retrieve the current
 * authentication token (API key, SAML, or OIDC).
 * 
 * Environment Variables:
 *   CLOUDSMITH_OIDC_SLUG - Organization slug for OIDC authentication
 *   CLOUDSMITH_API_KEY - API key (fallback if not using OIDC/SAML)
 */
fun getCloudsmithToken(): String {
    val oidcSlug = System.getenv("CLOUDSMITH_OIDC_SLUG")
    val cmd = mutableListOf("cloudsmith", "tokens", "get")
    
    if (oidcSlug != null && oidcSlug.isNotEmpty()) {
        cmd.addAll(listOf("--oidc-slug", oidcSlug))
    }
    
    return try {
        val stdout = ByteArrayOutputStream()
        exec {
            commandLine = cmd
            standardOutput = stdout
        }
        stdout.toString().trim()
    } catch (e: Exception) {
        throw GradleException("Failed to get Cloudsmith token: ${e.message}")
    }
}

// Example repository configuration
repositories {
    maven {
        name = "Cloudsmith"
        url = uri("https://maven.cloudsmith.io/my-org/my-repo/")
        credentials {
            username = "token"
            password = getCloudsmithToken()
        }
    }
}

// Example publishing configuration
publishing {
    repositories {
        maven {
            name = "Cloudsmith"
            url = uri("https://maven.cloudsmith.io/my-org/my-repo/")
            credentials {
                username = "token"
                password = getCloudsmithToken()
            }
        }
    }
}
