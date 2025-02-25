package buildTypes

import jetbrains.buildServer.configs.kotlin.BuildType
import jetbrains.buildServer.configs.kotlin.DslContext
import jetbrains.buildServer.configs.kotlin.ParameterDisplay
import jetbrains.buildServer.configs.kotlin.buildSteps.python
import jetbrains.buildServer.configs.kotlin.triggers.vcs

object BuildAssets : BuildType({
    name = "Build Assets"
    description = "Build game assets"

    artifactRules = "%output_dir%"

    params {
        text(
            "output_dir",
            "%teamcity.build.checkoutDir%/.result",
            label = "Path to output directory",
            allowEmpty = false,
        )
        text(
            "assets_dir",
            "%teamcity.build.checkoutDir%/assets",
            label = "Path to assets directory",
            allowEmpty = false,
        )
        text(
            "revision",
            "%build.vcs.number%",
            label = "Git hash",
            allowEmpty = false,
        )
        text(
            "agent_name",
            "LT1-CXBUILD-101-D",
            display = ParameterDisplay.HIDDEN,
            allowEmpty = false,
        )
    }

    vcs {
        root(DslContext.settingsRoot)
    }

    steps {
        python {
            name = "Build assets"
            id = "python_runner"
            workingDir = "scripts"
            environment = venv {
                requirementsFile = "%teamcity.build.checkoutDir%/scripts/requirements.txt"
            }
            command = file {
                filename = "build_assets.py"
                scriptArguments = "--assets-dir %assets_dir% --output-dir %output_dir% --revision=%revision%"
            }
        }
    }

    triggers {
        vcs {
            triggerRules = "+:assets"
            branchFilter = ""
            perCheckinTriggering = true
            enableQueueOptimization = false
        }
    }

    requirements {
        equals("teamcity.agent.name", "%agent_name%")
    }
})