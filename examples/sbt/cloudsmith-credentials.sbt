import scala.sys.process._
import scala.util.Try

/**
 * Cloudsmith Credential Resolver for sbt
 * 
 * Add this to your build.sbt or ~/.sbt/1.0/credentials.sbt
 * 
 * This resolver fetches credentials dynamically from the Cloudsmith CLI.
 */

// Function to get Cloudsmith token
lazy val getCloudsmithToken: String = {
  val oidcSlug = sys.env.get("CLOUDSMITH_OIDC_SLUG")
  val cmd = oidcSlug match {
    case Some(slug) => Seq("cloudsmith", "tokens", "get", "--oidc-slug", slug)
    case None => Seq("cloudsmith", "tokens", "get")
  }
  
  Try(cmd.!!.trim).getOrElse {
    sys.error("Failed to get Cloudsmith token. Ensure cloudsmith CLI is installed.")
  }
}

// Credentials for Cloudsmith Maven repository
credentials += Credentials(
  "Cloudsmith",
  "maven.cloudsmith.io",
  "token",
  getCloudsmithToken
)

// Example resolver configuration
resolvers += "Cloudsmith" at "https://maven.cloudsmith.io/my-org/my-repo/"

// Example publishing configuration
publishTo := Some("Cloudsmith" at "https://maven.cloudsmith.io/my-org/my-repo/")
