# Make Cooked Editor As DLC

> This plugin is used in conjunction with the MakeCookedEditor UAT script to generate a cooked editor as a DLC add-on to a cooked client. It does not need to be enabled.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器DLC生成器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器配置） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MakeCookedEditorAsDLC) | |

## 用途

此插件本身不包含可执行代码，它是一个**配置和标记插件**。其核心目的是为 `MakeCookedEditor` UAT（Unreal Automation Tool）脚本提供必要的配置和上下文。该脚本用于将 Unreal Editor 的核心功能打包、烘焙（Cook）成一个可加载的 DLC（DownLoadable Content）包。

它解决的问题是：如何将编辑器本身的功能模块化，并以 DLC 的形式附加到一个已烘焙的客户端（Cooked Client）上。这样，客户端可以保持精简，而完整的编辑器功能可以通过单独的 DLC 包进行分发和更新，实现编辑器与客户端的分离部署。

## 使用场景

- 你正在开发一个需要将编辑器功能作为可选组件分发的引擎或工具链。
- 你需要构建一个“烘焙的编辑器”（Cooked Editor），该编辑器能够附加到特定的烘焙客户端上运行，而不是作为独立的完整编辑器启动。
- 你的工作流程涉及使用 UAT 脚本自动化编辑器打包过程。

## 蓝图用法

此插件主要面向引擎构建和打包流程，**不暴露任何蓝图可调用的函数（BlueprintCallable）或属性（BlueprintReadWrite）**。其配置通过 `.uplugin` 文件和关联的 UAT 脚本完成。

## C++ 用法

此插件不包含 C++ 模块，因此没有直接的头文件或 C++ API。其作用通过 UAT 脚本在引擎构建流程中体现。要使用其功能，你通常通过命令行调用 UAT 脚本：

```bash
# 典型的 UAT 调用命令（在命令行或构建脚本中使用）
RunUAT MakeCookedEditor -Project=<YourProject.uproject> -Cook -Stage -DLC=MakeCookedEditorAsDLC
```

## Demo 示例

此插件的“示例”体现在其使用流程中，而非独立的可运行代码。以下是一个概念性的命令行流程：

```bash
# 步骤1：确保插件存在于引擎的 Plugins/Editor 目录下。
# 步骤2：执行 UAT 命令，指定此插件作为 DLC 来源。
RunUAT MakeCookedEditor -Project=MyGame.uproject -DLC=Engine/Plugins/Editor/MakeCookedEditorAsDLC -Cook -Stage -Package

# 此命令会：
# 1. 使用 MakeCookedEditor UAT 脚本。
# 2. 将引擎和项目的编辑器部分烘焙成资产。
# 3. 将 MakeCookedEditorAsDLC 插件指定为额外的 DLC 模块。
# 4. 最终输出一个包含烘焙编辑器功能的 DLC 包，可以附加到烘焙后的客户端。
```

## 模块依赖

此插件本身无特殊依赖（仅标准 Core/Engine/Slate 等）。它的价值在于作为 `MakeCookedEditor` UAT 脚本的**输入和配置**，而非一个运行时或编辑时依赖项。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议。 |
| 2021-09-29 | `1ee4eed9` | Merge from Release-Engine-Test @ 17666640 to UE5/Main ... | 插件随UE5代码库首次合并创建。 |

### 维护评价

此插件自2021年9月创建以来，仅在2022年10月有过一次安全链接更新，此后再无活动。最近的实质性功能性更新日期距今已超过2年。

- **创建时间**：约4年前（2021年）。
- **更新频率**：极低，仅有一次安全修复。
- **活跃度**：可能处于维护不活跃或仅保持基础编译通过的状态。
- **已知问题**：作为配置插件，主要风险在于依赖的 UAT 脚本 (`MakeCookedEditor`) 是否与当前引擎版本兼容。
- **推荐使用**：仅在你明确需要使用 `MakeCookedEditor` 工作流程且经过验证在你当前引擎版本下可用时，才需要关注此插件。对于常规的编辑器开发或打包，无需启用或了解此插件。

**警告**：该插件最近一次功能性更新（首次创建）距今已超过2年，维护可能不活跃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/MakeCookedEditorAsDLC)