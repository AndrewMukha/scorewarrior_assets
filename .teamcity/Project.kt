import buildTypes.BuildAssets
import jetbrains.buildServer.configs.kotlin.Project
import vcsRoots.root

object Project : Project({
    description = "Assets Builder"

    vcsRoot(root)

    buildType(BuildAssets)
})