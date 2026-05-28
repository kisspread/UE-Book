# Python Editor Script Plugin

> Python integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Python 脚本插件 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 示例脚本、Blueprint 节点资产） |
| 模块 | `PythonScriptPluginPreload` (Runtime), `PythonScriptPlugin` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-12-08 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin) | |

## 用途

PythonScriptPlugin 将完整的 CPython 解释器嵌入到 Unreal Editor 中，让开发者可以使用 Python 脚本直接操控 Unreal Engine 的反射系统——包括所有暴露的 UObject、UScriptStruct、UEnum、UFunction、FProperty 等。

它解决的核心问题是：**为 Technical Artist 和 Tools Programmer 提供一种高效的脚本化工作流**，用于批量资产处理、编辑器自动化、Pipeline 工具开发，以及需要快速迭代的原型开发。与蓝图相比，Python 更适合处理数据密集型操作和命令行批处理任务。

## 使用场景

- 你需要批量重命名/移动/转换大量资产 → 用 Python 脚本遍历 AssetRegistry 并自动化操作
- 你需要在 CI/CD Pipeline 中通过命令行驱动编辑器 → 用 `UnrealEditor-Cmd -ExecutePythonScript` 运行脚本
- 你需要构建自定义编辑器工具和菜单 → 通过 Python 注册 EditorUtilityWidget 和 ToolMenus
- 你需要从外部应用远程控制编辑器 → 启用 Remote Execution，通过 TCP/UDP 连接发送命令
- 你需要在编辑器 REPL 控制台中快速测试 API → 直接在 Output Log 窗口输入 Python 代码
- 你需要自动生成重复性的关卡/资产数据 → 用 Python 脚本直接创建 Actor、设置属性

## 模块文档

本插件包含两个子模块和多个功能子系统，详细文档见下表：

| 文档 | 内容 |
|---|---|
| [核心 API 与蓝图用法](Core-API.md) | PythonScriptLibrary、状态检查、命令执行、蓝图节点 |
| [类型包装系统](Type-Wrapping.md) | UObject/UStruct/UEnum/Delegate 到 Python 类型的映射与工厂系统 |
| [类型生成与注册](Type-Generation.md) | PyWrapperTypeRegistry、从 Python 定义 UE 类型（UClass/UEnum） |
| [容器与基础类型](Container-Types.md) | Array/Set/Map/FixedArray/Name/Text/FieldPath 的 Python 包装 |
| [设置与配置](Settings.md) | 插件设置、开发者模式、PipInstall、Remote Execution |
| [其他子系统](Subsystems.md) | PipInstall、RemoteExecution、PyReferenceCollector、K2Node |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Python Available` | 检查当前环境是否支持 Python | `UPythonScriptLibrary` |
| `Is Python Configured` | 检查 Python 是否已配置 | `UPythonScriptLibrary` |
| `Is Python Initialized` | 检查 Python 是否已初始化并可用 | `UPythonScriptLibrary` |
| `Force Enable Python At Runtime` | 强制在运行时启用 Python | `UPythonScriptLibrary` |
| `Execute Python Command` | 执行 Python 代码或文件 | `UPythonScriptLibrary` |
| `Execute Python Command (Advanced)` | 高级执行，可获取命令结果和日志输出 | `UPythonScriptLibrary` |
| `Execute Python Script` | 带输入/输出参数绑定的 Python 脚本执行节点 | `UPythonScriptLibrary` |
| `Set Keep Python Script Alive` | 设置命令行脚本执行后是否保持编辑器运行 | `UEditorPythonScriptingLibrary` |
| `Get Keep Python Script Alive` | 获取当前脚本保活状态 | `UEditorPythonScriptingLibrary` |

### 使用示例（蓝图描述）

**简单脚本执行**：
1. 拖入 `Execute Python Command` 节点
2. 在 `PythonCommand` 输入框中填入 `print("Hello from UE!")`
3. 连接执行线到需要触发的事件

**高级脚本执行（获取结果）**：
1. 拖入 `Execute Python Command (Advanced)` 节点
2. 设置 `ExecutionMode` 为 `EvaluateStatement`
3. 在 `PythonCommand` 中填入 `1 + 1`
4. `CommandResult` 输出将为 `"2"`
5. `LogOutput` 数组包含执行期间所有日志

**带参数的 Python 脚本**：
1. 拖入 `Execute Python Script` 节点
2. 在编辑器详情面板中设置 `Inputs` 和 `Outputs` 参数名
3. 连接输入/输出 Pin 到其他节点
4. 节点会自动将输入参数注入到 Python 脚本的 `locals()` 中

## C++ 用法

### 头文件引入

```cpp
#include "PythonScriptTypes.h"
#include "IPythonScriptPlugin.h"
```

### 基本用法

```cpp
// 检查 Python 是否可用
IPythonScriptPlugin* PythonPlugin = IPythonScriptPlugin::Get();
if (PythonPlugin && PythonPlugin->IsPythonInitialized())
{
    // 执行简单 Python 命令
    PythonPlugin->ExecPythonCommand(TEXT("print('Hello from C++!')"));
}
```

来源：`Public/IPythonScriptPlugin.h`

### 高级用法（带结果捕获）

```cpp
// 使用 FPythonCommandEx 获取执行结果和日志
FPythonCommandEx Command;
Command.Command = TEXT("unreal.EditorAssetLibrary.list_assets('/Game/MyFolder', True, False)");
Command.ExecutionMode = EPythonCommandExecutionMode::ExecuteFile;
Command.FileExecutionScope = EPythonFileExecutionScope::Private;
Command.Flags = EPythonCommandFlags::None;

bool bSuccess = PythonPlugin->ExecPythonCommandEx(Command);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Command result: %s"), *Command.CommandResult);
    for (const FPythonLogOutputEntry& LogEntry : Command.LogOutput)
    {
        UE_LOG(LogTemp, Log, TEXT("[%s] %s"), LexToString(LogEntry.Type), *LogEntry.Output);
    }
}
```

来源：`Public/PythonScriptTypes.h`、`Public/IPythonScriptPlugin.h`

### 响应回调注册

```cpp
// 注册 Python 初始化后的回调
IPythonScriptPlugin* PythonPlugin = IPythonScriptPlugin::Get();
PythonPlugin->RegisterOnPythonInitialized(FSimpleDelegate::CreateLambda([]()
{
    // Python 已就绪，可以安全调用 Python 命令
    UE_LOG(LogTemp, Log, TEXT("Python is ready!"));
}));
```

来源：`Public/IPythonScriptPlugin.h`

## Demo 示例

### PythonObjectHandle 的使用

当需要在 Python 生成的 UE 类型中存储任意 Python 对象引用时，使用 `UPythonObjectHandle`：

```cpp
// MyPythonTool.h
#pragma once
#include "CoreMinimal.h"
#include "PythonScriptPlugin/Private/PyWrapperBase.h"  // for UPythonObjectHandle

class FMyPythonTool
{
public:
    /** 创建一个 Python 对象句柄并存储 Python 可调用对象 */
    static void StorePythonCallable(PyObject* InCallable)
    {
        UPythonObjectHandle* Handle = UPythonObjectHandle::Create(InCallable);
        // Handle 可以作为 UPROPERTY 存储在任意 UObject 上
    }

    /** 解析句柄获取原始 Python 对象 */
    static PyObject* ResolveStoredHandle(UPythonObjectHandle* Handle)
    {
        if (Handle)
        {
            return Handle->Resolve();  // 返回 borrowed reference，或 Py_None
        }
        return nullptr;
    }
};
```

来源：`Private/PyWrapperBase.h`（`UPythonObjectHandle` 类定义）

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ContentBrowserFileDataSource` | 在 Content Browser 中显示 Python 文件（仅 LiveLinkHub 程序） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。PythonScriptPluginPreload 模块用于在最早期加载阶段注册 Python 库路径。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `2d500e32` | Python-defined function return value fixes | 修复 Python 定义函数返回值的问题 |
| 2026-04-14 | `a65e136c` | [UEFN] Add allow list for Python startup scripts UEFN | 为 UEFN 添加 Python 启动脚本路径白名单 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-13 | `895825ca` | [Backout] - CL52634718 | 回退之前的提交 |
| 2026-04-13 | `d6c3836d` | [UEFN] Add allow list for Python startup scripts. | 添加 Python 启动脚本路径白名单功能 |

### 维护评价

- **创建时间**：2017 年 12 月，已有 8 年以上历史
- **仍为实验性**：`IsBetaVersion=true`、`EnabledByDefault=false`，需要手动启用
- **持续活跃**：2026 年 4 月仍有功能性更新（返回值修复、UEFN 白名单支持），说明 Epic 仍在积极维护
- **社区广泛使用**：作为 UE 中唯一的官方 Python 集成方案，被大量技术美术和管线工具开发者使用
- **已知限制**：仅在编辑器环境可用（UncookedOnly），不支持运行时打包；默认关闭需手动启用
- **推荐程度**：✅ **强烈推荐**用于编辑器自动化和管线工具开发。虽然是实验性标签，但已经经过多年打磨，API 稳定。对于编辑器内 Python 脚本需求，这是唯一官方选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Tests)