# Procedural Content Generation Framework (PCG) Python Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Editor Python Interpreter.

| 属性 | 值 |
|---|---|
| 中文名 | PCG Python 桥接 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码资产） |
| 模块 | `PCGPythonInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop) | |

## 用途

此插件为UE的程序化内容生成（PCG）框架提供了与编辑器内置Python解释器交互的能力。它允许用户在PCG图（Graph）中直接执行Python脚本，将PCG数据（如点、属性）传入脚本进行处理，并将处理后的结果输出回PCG流程。这解决了在程序化工作流中需要编写复杂自定义逻辑、调用外部Python库或进行数据批处理的需求，极大地扩展了PCG框架的灵活性和能力边界。

## 使用场景

- 你正在使用PCG框架生成游戏世界，但需要一个标准节点无法实现的复杂数据处理算法 → 使用 `Execute Python Script` 节点在PCG图内直接编写或调用该Python算法。
- 你需要将PCG生成的点云数据导出为外部格式（如CSV、GeoJSON）进行分析或用于其他DCC工具 → 使用Python脚本读取PCG数据并执行文件写入操作。
- 你想利用Python的科学计算库（如NumPy, Pandas）对PCG属性数据进行批量数学运算或统计分析。
- 你希望在PCG流程中实现一个快速原型或迭代，Python的快速开发周期比编写C++节点更高效。

## 蓝图用法

此插件主要通过在PCG编辑器中添加特定节点来使用，而非在游戏运行时蓝图中直接调用。核心的可调用函数（`BlueprintCallable`）集中在数据桥接类中，供Python脚本内部调用。

### 核心节点与设置

在PCG编辑器中，你可以找到并添加以下节点：

| 节点/设置 | 说明 | 所在类 |
|---|---|---|
| `Execute Python Script` | PCG图节点。从输入数据属性、内联代码或`.py`文件执行Python脚本。 | `UPCGExecutePythonScriptSettings` |
| `Python Data Processor` | PCG图节点。拥有动态输入输出引脚，允许Python脚本直接访问和构建完整的 `FPCGDataCollection`。 | `UPCGPythonDataProcessorSettings` |
| `Get Input Collection` | 供Python脚本调用。获取当前节点的输入PCG数据集合。 | `UPCGPythonDataBridge` |
| `Set Output Collection` | 供Python脚本调用。将脚本构建的输出PCG数据集合设置回节点。 | `UPCGPythonDataBridge` |
| `Add To Collection` | 供Python脚本调用。将单个 `UPCGData` 对象添加到输出集合中，可指定引脚标签和标签。 | `UPCGPythonDataBridge` |

**节点设置属性（在PCG节点细节面板中）：**
- `ScriptInputMethod`: 选择脚本来源（`Input` 从数据读取，`File` 从文件读取）。
- `ScriptSource`: 当来源为`Input`时，指定用哪个属性作为脚本文本。
- `ScriptPath`: 当来源为`File`时，指定`.py`文件的路径。
- `bMuteEditorToast`: 是否静默执行过程中的编辑器通知。
- `InlineScript`: （内部属性）当使用内联默认值时，此处的字符串为默认脚本内容。

### 使用示例（蓝图描述）

1.  **创建PCG图**：在内容浏览器中创建新的 `PCG Graph` 资产。
2.  **添加节点**：从节点菜单搜索 “`Execute Python Script`” 并添加到图表中。可以为其连接输入数据（如一个点集生成器）。
3.  **配置脚本**：在节点的细节面板中，将 `ScriptInputMethod` 设置为 `Input`。此时会出现一个 `ScriptSource` 选择器，你可以选择使用输入数据中的某个属性。或者，将其设置为 `File` 并指定一个本地的Python脚本路径。
4.  **编写脚本**：在 `ScriptSource` 指向的属性中，或`.py`文件里，编写你的Python代码。脚本会通过 `unreal.PCGPythonDataBridge` 类与PCG数据交互。
5.  **连接输出**：执行节点后，其输出引脚将携带处理后的PCG数据，可以连接到后续的PCG节点。

## C++ 用法

此插件主要提供编辑器内PCG节点，C++层的直接使用较少。扩展功能通常围绕数据桥接类 `UPCGPythonDataBridge` 进行。

### 头文件引入

```cpp
// 使用PCG数据桥接类
#include "Helpers/PCGPythonDataBridge.h"
```

### 基本用法

以下示例展示了如何在C++中模拟或扩展 `UPCGPythonDataBridge` 的使用逻辑（通常这部分工作由插件内部节点自动完成，用户Python脚本通过反射调用）。

```cpp
// 示例：假设在自定义的PCG节点执行逻辑中，初始化数据桥接以供Python使用
// 来源文件: Elements/PCGPythonDataProcessor.cpp (插件内部逻辑)
#include "Helpers/PCGPythonDataBridge.h"

void SomePCGNodeExecution(FPCGContext* Context)
{
    // 1. 获取或创建数据桥接对象（通常插件内部会为每次执行创建唯一实例）
    UPCGPythonDataBridge* Bridge = NewObject<UPCGPythonDataBridge>();
    
    // 2. 用当前节点的输入数据初始化桥接
    Bridge->Initialize(Context->InputData);
    
    // 3. 在此之后，Python脚本（通过某种方式执行）可以调用Bridge上的方法
    // 例如在Python中: bridge = unreal.find_object("PCGPythonDataBridge_..."); bridge.get_input_collection()
    
    // 4. 检查Python脚本是否设置了输出
    if (Bridge->HasOutputCollection())
    {
        // 5. 获取输出并传递到下一个PCG节点
        Context->OutputData = Bridge->GetOutputCollection();
    }
}
```

### 进阶用法

创建一个自定义的PCG节点，该节点在执行Python脚本前后对数据进行预处理和后处理。

```cpp
// 示例：自定义节点，对输入点进行筛选后再交给Python处理
// 假设你创建了一个继承自UPCGSettings的自定义设置类
#include "PCGSettings.h"
#include "Helpers/PCGPythonDataBridge.h"

class UMyCustomPCGPythonNode : public UPCGSettings
{
    // ... 其他设置 ...
    
    // 自定义属性：点密度阈值
    UPROPERTY(EditAnywhere, Category = "Filter")
    float DensityThreshold = 0.5f;
    
    virtual FPCGElementPtr CreateElement() const override;
};

// 对应的执行元素
class FMyCustomPCGPythonNodeElement : public IPCGElement
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        // 1. 预处理：根据DensityThreshold筛选输入点
        FPCGDataCollection FilteredInput = FilterPointsByDensity(Context->InputData, DensityThreshold);
        
        // 2. 初始化Python数据桥接（使用过滤后的数据）
        UPCGPythonDataBridge* Bridge = NewObject<UPCGPythonDataBridge>();
        Bridge->Initialize(FilteredInput);
        
        // 3. 执行用户的Python脚本（逻辑同插件内置节点，此处省略）
        // ExecutePythonScript(Bridge, ...);
        
        // 4. 后处理：如果Python未设置输出，则使用原始过滤数据作为输出
        if (Bridge->HasOutputCollection())
        {
            Context->OutputData = Bridge->GetOutputCollection();
        }
        else
        {
            Context->OutputData = FilteredInput;
        }
        
        return true;
    }
    
private:
    FPCGDataCollection FilterPointsByDensity(const FPCGDataCollection& Input, float Threshold) const
    {
        // 实现具体的点筛选逻辑...
        return FilteredData;
    }
};
```

## Demo 示例

此插件的使用主要通过蓝图（PCG图）节点。一个典型的蓝图使用流程如下：

**目标**：使用Python脚本为PCG生成的每个点计算一个基于其Z坐标的“高度等级”属性。

1.  **创建PCG图资产**。
2.  **添加一个点集生成器节点**（如 `Surface Sampler`）作为输入源。
3.  **添加 `Execute Python Script` 节点**，并连接到点集生成器的输出。
4.  **配置该节点**：
    - `ScriptInputMethod` 设置为 `Input`。
    - `ScriptSource` 选择一个字符串类型的输入属性，或者直接在节点上设置一个 `InlineScript` 默认值。
5.  **在Python脚本内容中编写**：
```python
import unreal

# 获取数据桥接对象（由插件节点在执行时自动创建并命名）
bridge = unreal.find_object("PCGPythonDataBridge")

# 获取输入点数据
input_collection = bridge.get_input_collection()
if input_collection.is_empty():
    bridge.set_output_collection(input_collection)
    exit()

# 处理第一个点数据集（假设只有一个）
point_data = input_collection.get_data(0)
point_count = point_data.get_num_points()

# 为每个点计算并设置新属性
heights = point_data.get_vector_attribute("Position") # 假设位置是向量属性
levels = ["Low", "Medium", "High"]
new_level_attribute = unreal.PCGDataAttributeString()

for i in range(point_count):
    z_height = heights[i].z
    if z_height < 100:
        level = levels[0]
    elif z_height < 200:
        level = levels[1]
    else:
        level = levels[2]
    new_level_attribute.values.append(level)

# 创建输出数据（这里直接修改原数据，实际应创建新PCGData）
# ... 此处省略将new_level_attribute添加到point_data属性集的步骤 ...
# 假设我们直接传递修改后的input_collection
bridge.set_output_collection(input_collection)

print("Python script executed successfully.")
```
6.  **运行PCG图**，观察 `Execute Python Script` 节点的输出，其中的点数据应已包含计算好的“高度等级”字符串属性。

## 模块依赖

此插件依赖于PCG框架和Python脚本插件。要在你的模块中使用其功能，需要在 `.Build.cs` 文件中添加依赖。

| 模块 | 用途 |
|---|---|
| `PCG` | 提供PCG框架核心类、数据结构（如 `FPCGDataCollection`, `UPCGData`）和节点基类。 |
| `PythonScriptPlugin` | 提供编辑器内Python解释器运行环境和与UE对象的交互能力。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `d47477a3` | [PCG] Python Data Processor Node | 新增了 `Python Data Processor` 节点，支持动态引脚和直接数据集合操作。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 `UE_LOG` 迁移到新的 `UE_LOGF`，属于内部维护性更新。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 移除了过时的 `TStringBuilderBase` 构造，属于底层代码清理。 |
| 2025-08-22 | `2de17507` | [PCG] Fixed bug causing Inline Constant not to respect required pin | 修复了一个导致内联常量不尊重必需引脚状态的Bug。 |
| 2025-07-14 | `002e7b67` | [PCG] Python Interop Plugin and Execute Python Script Node | 插件的首次创建，包含核心的 `Execute Python Script` 节点。 |

### 维护评价

**综合评价：实验性，维护活跃，但使用需谨慎。**

- **状态**：插件创建于2025年7月，最近一次功能更新在2026年4月（`d47477a3`），表明仍在积极开发中。`.uplugin` 标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，明确指出这是一个实验性功能。
- **维护**：从提交记录看，除了初始提交外，后续有修复、重构和重要的功能新增（如 `Python Data Processor` 节点），维护比较活跃。
- **推荐**：由于是Beta版本，API和行为可能在未来版本中发生变化。**推荐用于原型开发、内部工具链或实验性项目**。不推荐直接用于需要长期稳定性的核心游戏逻辑中。使用时需注意依赖的 `PythonScriptPlugin` 本身也是编辑器功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG框架文档，其中可能包含此插件的用法)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop/Tests) (如果存在)