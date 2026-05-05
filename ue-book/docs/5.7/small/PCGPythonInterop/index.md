# Procedural Content Generation Framework (PCG) Python Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Editor Python Interpreter.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否（`EnabledByDefault: false`） |
| 包含内容 | ✅ 是 |
| 模块 | PCGPythonInteropEditor (Editor) |
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCGInterops/PCGPythonInterop) | |

## 用途

PCGPythonInterop 在 PCG 图表（PCG Graph）和编辑器内置的 Python 解释器之间架起桥梁。它提供了一个 **Execute Python Script** 节点，让你可以在 PCG 图表的执行流程中运行 Python 脚本。

简单来说：PCG 擅长程序化内容生成，Python 擅长通用脚本逻辑。这个 plugin 让你把两者串联起来——在 PCG 图表的某个环节执行 Python 脚本，利用 Python 的灵活性来完成 PCG 原生节点不方便做的事。

## 使用场景

- 你在用 PCG 图表做程序化关卡生成，需要在某个步骤调用 Python 脚本来处理数据、调用外部 API 或执行复杂的字符串/文件操作 → 在 PCG 图表中添加 **Execute Python Script** 节点
- 你有一个现成的 Python 工作流（例如地形数据处理、资产批量修改），想把它嵌入到 PCG 生成管线中 → 用 File 模式指向你的 `.py` 文件
- 你需要在 PCG 生成过程中动态执行从上游节点传递过来的 Python 代码 → 用 Input 模式，通过 Source pin 传入脚本字符串

## 蓝图用法

本 plugin 不提供蓝图节点。它提供的是 **PCG 图表节点**，在 PCG 编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Execute Python Script | 执行 Python 脚本（内联、输入或文件） | `UPCGExecutePythonScriptSettings` |

### 节点属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `ScriptInputMethod` | `EPCGPythonScriptInputMethod` | 脚本来源方式：`Input`（从输入引脚/内联）或 `File`（从 .py 文件） |
| `ScriptSource` | `FPCGAttributePropertyInputSelector` | Input 模式下，指定从哪个属性读取脚本内容（仅 Input 模式可见） |
| `ScriptPath` | `FFilePath` | File 模式下，指定 .py 文件路径（仅 File 模式可见） |
| `bMuteEditorToast` | `bool` | 是否静默编辑器 Toast 通知 |

### 引脚配置

**输入引脚：**

| 引脚名 | 数据类型 | 说明 |
|---|---|---|
| `Source` | `Param` | 仅 Input 模式出现。接收包含 Python 脚本代码的 FString 属性。如果未连接，使用节点上的内联默认值 |

**输出引脚：**

| 引脚名 | 数据类型 | 说明 |
|---|---|---|
| `ExecutionDependency` | `Any` | 纯依赖引脚（DependencyOnly），不传递数据，仅用于控制执行顺序 |

### 使用示例（PCG 图表描述）

**示例 1：使用内联脚本**

1. 在 PCG 图表中添加 **Execute Python Script** 节点
2. 保持 `ScriptInputMethod` 为 `Input`
3. 在 Source 引脚的默认值中直接编写 Python 代码（默认是 `print("Hello PCG World!")`）
4. 将节点连接到你的 PCG 流程中（通过 ExecutionDependency 引脚控制顺序）
5. 运行图表，Python 脚本将在该节点处执行

**示例 2：从 .py 文件执行**

1. 添加 **Execute Python Script** 节点
2. 将 `ScriptInputMethod` 设为 `File`
3. 在 `ScriptPath` 中选择你的 `.py` 文件
4. 连接到 PCG 流程中

**示例 3：从上游数据动态传入脚本**

1. 添加 **Execute Python Script** 节点，保持 Input 模式
2. 将包含 Python 脚本字符串的 Param 数据连接到 `Source` 引脚
3. 在 `ScriptSource` 属性中选择要读取的属性名
4. 上游数据中的每一行 FString 将被拼接为完整的 Python 脚本执行

## C++ 用法

本 plugin 是 Editor-only 的 PCG Settings 扩展，通常不需要直接在 C++ 中使用。以下内容来自源码分析。

### 头文件引入

```cpp
#include "Elements/PCGExecutePythonScript.h"
```

### 关键类

#### `UPCGExecutePythonScriptSettings`

继承自 `UPCGSettings` 和 `IPCGSettingsDefaultValueProvider`，是 PCG 图表中 "Execute Python Script" 节点的设置类。

```cpp
// 脚本输入方式
UENUM()
enum class EPCGPythonScriptInputMethod
{
    Input,  // 从输入数据或内联脚本执行
    File    // 从 .py 文件执行
};

// 核心属性
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings)
EPCGPythonScriptInputMethod ScriptInputMethod;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings,
    meta = (PCG_Overridable, EditCondition = "ScriptInputMethod == EPCGPythonScriptInputMethod::Input"))
FPCGAttributePropertyInputSelector ScriptSource;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings,
    meta = (PCG_Overridable, EditCondition = "ScriptInputMethod == EPCGPythonScriptInputMethod::File",
            FilePathFilter = "Python files (*.py)|*.py"))
FFilePath ScriptPath;

UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings, AdvancedDisplay,
    meta = (PCG_Overridable))
bool bMuteEditorToast = false;
```

#### `FPCGExecutePythonScriptElement`

实际执行逻辑所在的 Element 类。

```cpp
class FPCGExecutePythonScriptElement : public IPCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* InContext) const override;
    // 强制在主线程执行（Python 解释器要求）
    virtual bool CanExecuteOnlyOnMainThread(FPCGContext* Context) const override { return true; }
    // 不可缓存（每次执行都重新运行脚本）
    virtual bool IsCacheable(const UPCGSettings* InSettings) const override { return false; }
};
```

### 执行流程

来自 `PCGExecutePythonScript.cpp` 的核心逻辑：

```cpp
// 1. 获取 Python 解释器
const IPythonScriptPlugin* PythonModule = IPythonScriptPlugin::Get();
if (!PythonModule || !PythonModule->IsPythonAvailable())
{
    // 报错：Python 解释器不可用
    return true;
}

// 2. 根据 InputMethod 构建命令
FPythonCommandEx PythonSource{ .Flags = EPythonCommandFlags::None };

if (Settings->ScriptInputMethod == EPCGPythonScriptInputMethod::Input)
{
    // Input 模式：从 Source 引脚读取 FString 属性，拼接为脚本
    // 使用 EPythonCommandExecutionMode::ExecuteStatement
    PythonSource.ExecutionMode = EPythonCommandExecutionMode::ExecuteStatement;
}
else // File 模式
{
    // File 模式：直接将文件路径作为命令
    CommandBuilder = Settings->ScriptPath.FilePath;
}

// 3. 执行
PythonSource.Command = CommandBuilder.ToString();
IPythonScriptPlugin::Get()->ExecPythonCommandEx(PythonSource);

// 4. 错误处理：将 Python 日志转发到 PCG 日志系统
for (const FPythonLogOutputEntry& LogOutputEntry : PythonSource.LogOutput)
{
    // Info → Log, Warning → Warning, Error → Error
}
```

## Demo 示例

本 plugin 是纯 Editor 模块，不需要在你的项目中编写 C++ 代码。启用方式：

1. 打开 **Edit → Plugins**
2. 搜索 "PCG Python Interop"
3. 启用插件，重启编辑器
4. 在 PCG 图表中右键搜索 "Execute Python Script" 即可添加节点

### 最小 Python 脚本示例

在 Execute Python Script 节点的内联脚本中输入：

```python
import unreal

# 获取所有 Static Mesh Actor
actors = unreal.EditorLevelLibrary.get_all_level_actors()
sm_actors = [a for a in actors if isinstance(a, unreal.StaticMeshActor)]
print(f"Found {len(sm_actors)} Static Mesh Actors in the level")
```

### 文件模式示例

创建 `my_pcg_script.py`：

```python
import unreal

# 从 PCG 上下文中获取信息
print("[PCG Python] Script executed from file")

# 你可以在这里做任何 Python 能做的事：
# - 读写文件
# - 调用 Unreal Python API
# - 操作资产
# - 批量修改关卡数据
```

然后在节点中将 `ScriptInputMethod` 设为 `File`，`ScriptPath` 指向该文件。

## 模块依赖

### Plugin 依赖

| Plugin | 必需 | 说明 |
|---|---|---|
| `PCG` | ✅ | PCG 框架本身 |
| `PythonScriptPlugin` | ✅ | 提供编辑器内 Python 解释器 |

### 模块依赖（C++）

| 模块 | 类型 | 用途 |
|---|---|---|
| `Core` | Public | UE 核心库 |
| `CoreUObject` | Public | UObject 系统 |
| `Engine` | Public | 引擎核心 |
| `Projects` | Public | 项目管理 |
| `PCG` | Public | PCG 框架 |
| `PCGEditor` | Private (Editor) | PCG 编辑器 UI |
| `UnrealEd` | Private (Editor) | 编辑器功能 |
| `PythonScriptPlugin` | Private (Editor) | Python 解释器接口 |
| `AssetDefinition` | Private (Editor) | 资产定义 |
| `Slate` | Private (Editor) | UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-21 | `2de1750` | [PCG] Fixed bug causing Inline Constant not to respect required pin | 修复了内联常量不尊重 Required Pin 状态的 bug，属于核心功能修复 |
| 2025-07-14 | `002e7b6` | [PCG] Python Interop Plugin and Execute Python Script Node | 插件创建，初始实现 |

### 维护评价

- **创建时间**：2025-07-14，非常新的插件（🆕）
- **更新频率**：2 次 commit，间隔约 1 个月
- **实验性标记**：`IsBetaVersion: true`，`EnabledByDefault: false`
- **维护状态**：🆕 刚创建不久，处于早期开发阶段
- **已知限制**：
  - 仅 Editor 可用，不支持 Runtime（打包后不可用）
  - Python 执行强制在主线程，可能阻塞编辑器
  - 结果不可缓存，每次执行都重新运行
  - 输出引脚仅提供执行依赖，无法将 Python 结果传回 PCG 数据流
- **推荐程度**：适合实验和编辑器工具用途。作为 Beta 插件，API 可能变化。源码中的 `@todo_pcg` 注释表明 Epic 计划继续改进，包括：
  - 逐行反馈（`EvaluateStatement` 模式）
  - 参数输入/输出（类似 BP 和 HLSL 的参数传递）
  - 通用源码编辑器（统一 HLSL、Python 等脚本编辑体验）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCGInterops/PCGPythonInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
