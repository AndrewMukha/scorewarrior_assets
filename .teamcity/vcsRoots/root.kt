package vcsRoots

import jetbrains.buildServer.configs.kotlin.vcs.GitVcsRoot

object root : GitVcsRoot({
    name = "sw_root"
    pollInterval = 60
    url = "https://github.com/AndrewMukha/scorewarrior_assets.git"
    branch = "main"
    branchSpec = "+:refs/heads/*"
    checkoutPolicy = AgentCheckoutPolicy.USE_MIRRORS
    authMethod =
        password {
            userName = "scorewarrior"
            password = "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"
        }
})