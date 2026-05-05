# MakeCookedEditorAsDLC

> This plugin is used in conjunction with the MakeCookedEditor UAT script to generate a cooked editor as a DLC add-on to a cooked client. It does not need to be enabled.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | 无（纯标记插件） |
| 创建时间 | 2021-09-21 |
| 年龄标签 | 🆕 (约 4.5 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MakeCookedEditorAsDLC) | |

## 用途

MakeCookedEditorAsDLC 是一个**纯标记插件**（marker plugin），自身不包含任何 C++ 模块或蓝图逻辑。它的唯一存在意义是让 UAT（Unreal Automation Tool）的 `MakeCookedEditor` 构建脚本能识别到"已安装的编辑器插件需要被打包进 Cooked Editor"。

**核心问题**：当 UE5 将编辑器烘焙（cook）成一个可在运行时加载的 "Cooked Editor" 时，需要一种机制来确定哪些编辑器插件应该被包含。MakeCookedEditorAsDLC 的 `.uplugin` 文件就是这个机制的一部分——它作为一个可被构建系统扫描到的插件存在，配合 `CookedEditor.Automation.cs` 中的构建逻辑，确保 Cooked Editor 能正确组装。

**真正的核心代码**在 UAT 脚本中：
- [`Engine/Source/Programs/AutomationTool/CookedEditor/CookedEditor.Automation.cs`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Programs/AutomationTool/CookedEditor/CookedEditor.Automation.cs) — `MakeCookedEditor` 类，控制整个 Cooked Editor 的构建、烘焙和暂存流程
- [`Engine/Source/Programs/AutomationTool/CookedEditor/PlatformWrappers.cs`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Programs/AutomationTool/CookedEditor/PlatformWrappers.cs) — `WindowsCookedEditor`、`LinuxCookedEditor`、`MacCookedEditor` 等平台包装器

## 使用场景

- **你需要将编辑器烘焙成 DLC 包**：你的游戏已经用 `BasedOnReleaseVersion` 构建了一个发布版本（client），现在需要一个 "Cooked Editor" 作为该发布版本的 DLC 附加包来运行。Cooked Editor 可以在没有完整源码编译环境的机器上打开和编辑项目内容。
- **你需要一个 Cooked Cooker**：类似 Cooked Editor，但专门用于烘焙流程（`-cookedcooker` 模式），可以远程执行烘焙任务而无需完整引擎安装。
- **你需要在 QA 环境中使用编辑器**：Cooked Editor 可以在没有源码编译环境的 QA 机器上启动，用于验证内容。

## 蓝图用法

**无**。该插件不包含任何 C++ 模块、蓝图节点或可暴露的功能。它仅通过 UAT 命令行工具在构建流水线中被间接使用。

## C++ 用法

**无直接 C++ 用法**。该插件不包含源代码。

整个功能由 C# UAT 脚本实现，关键类如下：

### MakeCookedEditor（UAT 命令）

这是继承自 `BuildCommand` 的 UAT 命令类，通过命令行调用：

```bash
# 基本用法：为当前项目构建 Cooked Editor
RunUAT MakeCookedEditor -project=<YourProject.uproject>

# 构建 Cooked Cooker（用于远程烘焙）
RunUAT MakeCookedEditor -project=<YourProject.uproject> -cookedcooker

# 同时构建 Release 和 Cooked Editor（DLC 模式）
RunUAT MakeCookedEditor -project=<YourProject.uproject> -makerelease

# 将 Release 和 Cooked Editor 合并到同一目录
RunUAT MakeCookedEditor -project=<YourProject.uproject> -makerelease -CombineBuilds=<OutputPath>
```

### 配置（INI）

Cooked Editor 的行为通过项目的 `Game.ini` 中的 `[CookedEditorSettings]` 节控制：

```ini
[CookedEditorSettings]
; 是否将编辑器构建为已有 client 的 DLC
bBuildAgainstRelease=True

; DLC 插件名（当 bBuildAgainstRelease=True 时使用）
DLCPluginName=MyDLCPlugin

; Release 版本名称（默认为项目名）
ReleaseName=MyGame

; 目标类型：Game 或 Server
ReleaseTargetType=Game

; 自定义 Cooked Editor 的 Target 名称
CookedEditorTargetName=MyGameCookedEditor

; 自定义 Cooked Cooker 的 Target 名称
CookedCookerTargetName=MyGameCookedCooker

; 是否暂存 Shader 目录
bStageShaderDirs=True

; 是否暂存平台构建目录
bStagePlatformBuildDirs=True

; 是否暂存 Extras 目录
bStageExtrasDirs=False

; 是否暂存 UAT（用于 Cooked Cooker 运行时烘焙）
bStageUAT=False

; 地图模式：cooked / uncooked / none
MapMode=uncooked

; 是否暂存 Python 脚本
bStagePython=False

; 是否暂存 Collection 文件
bStageCollections=False

; 是否为外部分发（移除受限文件夹）
bIsForExternalDistribution=False
```

对于 **Cooked Cooker** 专用配置，使用 `[CookedEditorSettings_CookedCooker]` 节覆盖共享设置；Cooked Editor 专用配置使用 `[CookedEditorSettings_CookedEditor]` 节。

### 关键构建参数

MakeCookedEditor 在构建时会自动添加以下 Cooker 参数：

| 参数 | 说明 |
|---|---|
| `-ini:Engine:[Core.System]:CanStripEditorOnlyExportsAndImports=False` | 不剥离编辑器专用导出和导入 |
| `-ini:Engine:[AssetRegistry]:bSerializePackageData=True` | 在 AssetRegistry 中序列化包数据，以便 Cooker 定位资源 |
| `-AllowUnsafeBlueprintCalls` | 允许非编辑器 BP 引用编辑器 BP 的调用 |
| `-DlcReevaluateUncookedAssets` | DLC 模式下重新评估 base game 跳过的资源 |
| `-CookAgainstFixedBase` | DLC 模式下基于固定 base 进行烘焙 |

## 模块依赖

该插件本身无模块，无需任何 `Build.cs` 依赖。

要使用 Cooked Editor 构建功能，你的项目需要：
- UE5 引擎安装（包含 AutomationTool）
- 项目已配置 `CookedEditor` Target（如 `MyGameCookedEditor.Target.cs`）
- （DLC 模式）项目已配置 `BasedOnReleaseVersion`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2022-11-07 | `0a10c21ff628` | Update Release-Engine-Staging from UE5/Main — 引擎级批量更新，非针对该插件的改动 |
| 2021-09-21 | `4a45d1f034b3` | 初始添加 — 添加 CookedEditor TargetPlatform，支持将编辑器烘焙为完整构建或 DLC，添加 CookedEditor.Automation.cs 构建脚本，支持项目级 INI 配置覆盖 |

### 维护评价

- **创建时间**：2021-09-21（约 4.5 年前）
- **最后实质性更新**：2021-09-21（首次提交即为完整实现）
- **更新频率**：极低，仅有初始提交和一次引擎批量更新
- **推荐使用**：✅ 是。该插件本身是一个稳定的标记插件，功能无需迭代。实际的 Cooked Editor 构建逻辑在 `CookedEditor.Automation.cs` 中维护，该脚本随引擎版本持续更新。

该插件属于"一次创建，长期稳定"的类型。`.uplugin` 不需要修改，所有功能演进都在 UAT 脚本侧完成。**不需要担心维护状态**。

## 相关链接

- [源码（插件目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MakeCookedEditorAsDLC)
- [CookedEditor.Automation.cs（核心构建脚本）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Programs/AutomationTool/CookedEditor/CookedEditor.Automation.cs)
- [PlatformWrappers.cs（平台包装器）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Programs/AutomationTool/CookedEditor/PlatformWrappers.cs)
