# Python Editor Script Plugin

> Python integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Python 编辑器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PythonScriptPluginPreload` (Runtime), `PythonScriptPlugin` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin) | |

## 用途

PythonScriptPlugin 是 Unreal Editor 的 Python 语言集成插件。它解决了以下核心问题：

- 允许使用 Python 脚本直接操作 Unreal Editor 中的大部分功能（资产、蓝图、场景、UI 等）
- 为 Python 提供对 UE 反射系统的完整绑定（UObject、UStruct、UEnum、UFunction 等）
- 支持通过 pip 自动安装插件依赖的额外 Python 包
- 提供蓝图节点来在蓝图图表中执行 Python 脚本
- 支持在编辑器启动时自动执行 Python 脚本（通过命令行参数）

## 使用场景

- **编辑器自动化**：用 Python 批量处理资产重命名、导入/导出、材质替换等重复操作
- **测试与质量保证**：编写自动化测试脚本，模拟用户操作并验证编辑器状态
- **自定义工具开发**：快速开发不依赖 C++ 编译的编辑器工具，例如资产检查器、场景分析器
- **管线集成**：在项目构建过程中调用 Python 脚本，与外部 DCC 工具联动
- **教学与快速原型**：无需编译即可探索 UE 反射 API 的行为

## 蓝图用法

插件暴露了少量蓝图节点用于控制 Python 脚本的运行环境。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Keep Python Script Alive` | 设置是否在脚本执行完毕后保持编辑器进程运行（应用于命令行工具模式） | `UEditorPythonScriptingLibrary` |
| `Get Keep Python Script Alive` | 获取当前是否保持编辑器进程运行的标志 | `UEditorPythonScriptingLibrary` |
| `Execute Python Script` | （K2Node）在蓝图图表中执行一段 Python 脚本，支持自定义输入/输出参数 | `UK2Node_ExecutePythonScript` |

### 使用示例（蓝图描述）

**保持编辑器存活（命令行执行）**：
1. 在任意蓝图事件（如 `BeginPlay`）中连接 `Set Keep Python Script Alive` 节点
2. 将输入 `bNewKeepAlive` 设为 `true`
3. 脚本执行后编辑器不会自动关闭，直到再次调用 `Set Keep Python Script Alive(false)` 或调用 `SystemLibrary.quit_editor()`

**执行 Python 脚本（蓝图图表）**：
1. 右键图表搜索 "Execute Python Script" 节点
2. 在节点细节面板中，通过 `Inputs` 和 `Outputs` 数组定义自定义参数名（如 `MyInput`, `Result`）
3. 连接输入/输出引脚即可在蓝图中传递数据
4. 节点内部会调用 `unreal.execute_python_script()` 并自动映射参数

## C++ 用法

### 头文件引入

```cpp
#include "PythonScriptPlugin.h"
#include "PyCore.h"
#include "PyConversion.h"
```

### 基本用法

**在编辑器模块中获取 Python 脚本执行器**（来源：`Source/PythonScriptPlugin/Private/PythonScriptPlugin.cpp`）：

```cpp
// 获取插件实例
IPythonScriptPlugin& PythonPlugin = FPythonScriptPlugin::Get();

// 执行一段 Python 代码
const FString Code = TEXT("unreal.log('Hello from Python!')");
bool bResult = PythonPlugin.ExecPythonCommand(*Code);
```

**手动转换 Python 对象到 C++ 类型**（来源：`Private/PyConversion.h`）：

```cpp
PyObject* PyObj = ...; // 假设已获取
int32 OutValue = 0;

// 尝试将 Python 对象转换为 int32
FPyConversionResult Result = PyConversion::Nativize(PyObj, OutValue);
if (Result.Succeeded())
{
    UE_LOG(LogPython, Log, TEXT("Converted value: %d"), OutValue);
}
```

**使用作用域 GIL 保护**（来源：`Private/PyGIL.h`）：

```cpp
// 在非 Python 线程中操作 Python 对象时，需要持有 GIL
{
    FPyScopedGIL GIL;  // 自动获取 GIL 并确保释放
    // 在此作用域内安全调用 Python API
    PyObject* PyStr = PyUnicode_FromString("test");
    // ...
}
```

### 进阶用法

**注册自定义 Python 类型模块**（来源：`Private/PyCore.cpp`）：

```cpp
// 在模块启动阶段注册一个 Python 子模块
PyGenUtil::FNativePythonModule ModuleInfo;
ModuleInfo.PyModuleName = TEXT("my_tools");
ModuleInfo.PyModuleDoc = TEXT("Custom Python tools for my project");

// 初始化模块（会创建 Python 包装类型）
InitializePyWrapperBase(ModuleInfo);
InitializePyWrapperObject(ModuleInfo);
// ... 注册更多类型

// 将模块添加到主 unreal 命名空间
FPythonScriptPlugin::Get().AddPythonModule(ModuleInfo);
```

**使用类型转换辅助函数**（来源：`Private/PyConversion.h`）：

```cpp
// 将 C++ 对象转换为 Python 对象
UObject* MyObj = ...;
PyObject* PyObj = PyConversion::PythonizeObject(MyObj);
if (PyObj)
{
    // 使用 PyObj ...
    Py_DECREF(PyObj);
}
```

**使用 PyUtil 工具函数**（来源：`Private/PyUtil.h`）：

```cpp
// 将 Python 错误字符串转换为 UE FString
FString ErrorMsg = PyUtil::PyObjectToUEString(PyExc_TypeError);

// 创建 scoped slow task 反馈给用户
FPyScopedSlowTask* Task = FPyScopedSlowTask::New(&PyScopedSlowTaskType);
FPyScopedSlowTask::Init(Task, TEXT("Processing..."));
// ... 执行任务
FPyScopedSlowTask::Free(Task);
```

## Demo 示例

以下是一个完整的 C++ 示例，展示如何在编辑器模块中嵌入 Python 脚本执行并读取输出。

### PythonExecutor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "PythonScriptPlugin.h"

class FPythonExecutor
{
public:
    // 执行简单的 Python 表达式并返回结果
    static bool Eval(const FString& Code, FString& OutResult);
    
    // 加载并执行一个 .py 文件
    static bool RunFile(const FString& FilePath);
};
```

### PythonExecutor.cpp

```cpp
#include "PythonExecutor.h"
#include "PyConversion.h"
#include "PyUtil.h"

bool FPythonExecutor::Eval(const FString& Code, FString& OutResult)
{
    IPythonScriptPlugin& PythonPlugin = FPythonScriptPlugin::Get();
    if (!PythonPlugin.IsPythonAvailable())
    {
        OutResult = TEXT("Python not available.");
        return false;
    }

    // 执行代码，捕获 stdout
    // （实际执行会有回调，这里简化）
    bool bSuccess = PythonPlugin.ExecPythonCommand(*Code);
    
    // 获取最后一个 Python 的输出（非直接 API，示意）
    OutResult = bSuccess ? TEXT("OK") : TEXT("FAILED");
    return bSuccess;
}

bool FPythonExecutor::RunFile(const FString& FilePath)
{
    IPythonScriptPlugin& PythonPlugin = FPythonScriptPlugin::Get();
    if (!PythonPlugin.IsPythonAvailable()) return false;

    FString FileContent;
    if (!FFileHelper::LoadFileToString(FileContent, *FilePath))
    {
        return false;
    }
    return PythonPlugin.ExecPythonCommand(*FileContent);
}
```

## 模块依赖

从 `.uplugin` 和 `Build.cs` 分析，使用 PythonScriptPlugin 的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `ContentBrowserFileDataSource` | 提供对磁盘文件的文件数据源支持（插件依赖） |
| `Python3` | （隐式）嵌入的 Python 3 解释器库 |

**省略常见依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 2025-11-18 f928db93 Fix for crash in Python module during Shutdown when Python failed initializing
- 2025-10-08 5a0811f8 Allow UE to run if Python is not able to load properly
- 2025-09-26 cb970b02 Removed extra Python object when converting PyUnicode to FString
- 2025-09-12 ce6ff392 Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue
- 2025-08-27 b1317838 Exposed FTSTicker to Python
```

### 维护评价

- **创建时间**：2025 年 8 月（约 0 年）
- **更新频率**：每月均有功能性或修复性更新（最近 3 个月内 4 次提交）
- **活跃状态**：✅ 活跃维护。最新提交（2025-11-18）修复了关机崩溃，显示开发团队持续关注。
- **实验性标记**：插件标记为 `IsBetaVersion=true`，但实际使用已相当稳定。
- **推荐度**：强烈推荐。对于需要在 Unreal Editor 中进行脚本自动化的开发者来说，这是官方唯一支持的 Python 绑定方案。尽管标记为实验性，但功能完整、维护积极。

> **注意**：插件默认未启用（`EnabledByDefault=false`），需手动在 Plugin 管理器中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin/Source/PythonScriptPlugin/Private/Tests)（部分）