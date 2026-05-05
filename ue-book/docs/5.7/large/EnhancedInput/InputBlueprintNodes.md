# InputBlueprintNodes

> 蓝图节点模块：为 EnhancedInput 在蓝图编辑器中提供自定义 K2 节点、事件绑定和数据验证。

| 属性 | 值 |
|---|---|
| 模块类型 | UncookedOnly |
| 所属插件 | Enhanced Input |
| 模块路径 | `Engine/Plugins/EnhancedInput/Source/InputBlueprintNodes/` |
| 源文件数 | 17（8 .h + 8 .cpp + 1 Build.cs） |
| 创建时间 | 2022-03-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputBlueprintNodes) | |

## 用途

InputBlueprintNodes 模块是 Enhanced Input 插件的蓝图编辑器集成层。它不包含运行时逻辑，仅在编辑器的未打包模式（UncookedOnly）下加载。

该模块解决了以下核心问题：

1. **自定义蓝图事件节点**：为每个 `UInputAction` 资产自动生成"EnhancedInputAction xxx"事件节点，当玩家触发输入时执行对应的蓝图逻辑。
2. **输入值获取**：提供纯函数节点"Get xxx"，允许蓝图在任何时刻读取当前输入动作的值。
3. **调试键事件**：提供"Debug Key"节点，用于开发阶段通过键盘快捷键快速调试输入逻辑。
4. **资产拖拽支持**：允许将 `UInputAction` 资产从内容浏览器直接拖拽到蓝图图表中创建节点。
5. **Widget 蓝图验证**：确保使用了 Enhanced Input 的 Widget 蓝图正确设置了 `bAutomaticallyRegisterInputOnConstruction`。
6. **自动同步**：监听 `UInputAction` 的值类型和触发器变更，自动重建受影响的蓝图节点。

## 源码结构

```
InputBlueprintNodes/
├── InputBlueprintNodes.Build.cs                    # 模块构建配置
├── Public/
│   ├── InputBlueprintNodesModule.h                  # 模块头文件（无公开接口）
│   ├── K2Node_EnhancedInputAction.h                 # 输入动作事件节点
│   └── K2Node_GetInputActionValue.h                # 获取输入动作值节点
└── Private/
    ├── InputBlueprintNodesModule.cpp                # 模块启动、资产拖拽、自动同步
    ├── K2Node_EnhancedInputAction.cpp               # 事件节点实现（587 行，最大文件）
    ├── K2Node_EnhancedInputActionEvent.h/.cpp       # 编译期中间事件节点
    ├── K2Node_GetInputActionValue.cpp               # 获取值节点实现
    ├── K2Node_InputActionValueAccessor.h/.cpp       # 值访问器函数调用节点
    ├── K2Node_InputDebugKey.h/.cpp                  # 调试键事件节点
    ├── K2Node_InputDebugKeyEvent.h/.cpp             # 调试键编译期中间节点
    ├── EnhancedInputUserWidgetValidator.h/.cpp      # Widget 蓝图数据验证器
```

## 核心类

### UK2Node_EnhancedInputAction — 输入动作事件节点

这是蓝图编辑器中最核心的节点。在蓝图的"Input > Enhanced Action Events"菜单中为每个 `UInputAction` 资产注册一个事件节点。

**输出引脚（Output Pins）：**

| 引脚名 | 类型 | 说明 |
|---|---|---|
| 各 TriggerEvent（Triggered、Started、Ongoing、Completed、Canceled 等） | Exec | 每种 `ETriggerEvent` 对应一个执行引脚 |
| ActionValue | 动态类型（Bool/Double/Vector2D/Vector3） | 由 `InputAction->ValueType` 决定 |
| ElapsedSeconds | Double | 动作触发后的经过时间 |
| TriggeredSeconds | Double | 触发阶段的时间 |
| InputAction | Object | 对触发此事件的 InputAction 资产的引用 |

**关键特性：**

- **事件引脚可见性控制**：`Triggered` 引脚默认可见，其他引脚在高级视图中隐藏。可通过 `UEnhancedInputEditorSettings::VisibleEventPinsByDefault` 配置。
- **不支持的引脚警告**：当 Action 的 Trigger 不支持某个事件类型时，该引脚会被标记为 `(Unsupported)` 并在连接时给出警告。
- **防重复创建**：使用自定义 `UInputActionEventNodeSpawner`，同一蓝图中不会创建相同 InputAction 的重复节点，而是跳转到已有节点。
- **双击跳转**：双击节点会打开对应的 InputAction 资产编辑器。
- **Widget 蓝图支持**：在 Widget 蓝图中使用时，编译器会自动设置 `bAutomaticallyRegisterInputOnConstruction = true`。
- **编译展开（ExpandNode）**：编译时将用户友好的多引脚节点展开为多个 `UK2Node_EnhancedInputActionEvent` 中间节点，每个对应一个活跃的事件引脚，通过临时变量和赋值语句串联。

### UK2Node_GetInputActionValue — 获取输入动作值节点

纯函数节点（`IsNodePure = true`），在蓝图的"Input > Enhanced Action Values"菜单中注册。

**输出引脚：**

| 引脚名 | 类型 | 说明 |
|---|---|---|
| ReturnValue | 动态类型 | 由 `InputAction->ValueType` 决定的当前值 |

**值类型映射：**

| EInputActionValueType | 蓝图类型 |
|---|---|
| Boolean | Bool |
| Axis1D | Double |
| Axis2D | Vector2D |
| Axis3D | Vector3（Vector） |

**编译展开**：展开为 `UK2Node_InputActionValueAccessor`，内部调用 `UEnhancedInputLibrary::GetBoundActionValue`，自动连接 Self 节点作为 Actor 参数。

### UK2Node_InputDebugKey — 调试键事件节点

开发专用的调试节点，用于通过键盘快捷键触发输入事件。节点标题显示为"Debug Key [修饰键] 键名"。

**属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| InputKey | FKey | 绑定的键 |
| bExecuteWhenPaused | bool | 游戏暂停时是否执行 |
| bControl / bAlt / bShift / bCommand | bool | 修饰键组合 |

**输出引脚：**

| 引脚名 | 类型 | 说明 |
|---|---|---|
| Pressed | Exec | 键按下时触发 |
| Released | Exec | 键释放时触发 |
| Key | FKey | 触发的键名 |
| ActionValue | FInputActionValue | 输入动作值 |

**注意**：此节点标记为 `DevelopmentOnly`，在打包构建中不会执行。

### UK2Node_EnhancedInputActionEvent / UK2Node_InputDebugKeyEvent — 编译期中间节点

这两个类继承自 `UK2Node_Event`，不直接出现在蓝图编辑器中。它们是 `ExpandNode()` 生成的中间节点，在编译时将用户友好的节点展开为标准的事件委托绑定。

- `UK2Node_EnhancedInputActionEvent` → 绑定到 `UEnhancedInputActionDelegateBinding`
- `UK2Node_InputDebugKeyEvent` → 绑定到 `UInputDebugKeyDelegateBinding`

### UK2Node_InputActionValueAccessor — 值访问器节点

继承自 `UK2Node_CallFunction`，是 `UK2Node_GetInputActionValue` 展开后的中间节点。它调用 `UEnhancedInputLibrary::GetBoundActionValue`，并使用 `UEnhancedInputActionValueBinding` 进行动态绑定。

### UEnhancedInputUserWidgetValidator — Widget 蓝图验证器

继承自 `UEditorValidatorBase`，在数据验证（Data Validation）过程中检查 Widget 蓝图。

**验证逻辑**：
1. 仅验证 `UWidgetBlueprint` 类型资产
2. 检查 Widget 蓝图中是否有活跃的（已连接引脚的）`UK2Node_EnhancedInputAction` 节点
3. 如果有，则验证 `bAutomaticallyRegisterInputOnConstruction` 是否为 true
4. 如果为 false，报错要求用户手动设置

可通过 CVar `enhancedInput.bp.ShouldValidateWidgetBlueprintSettings` 关闭此验证。

## 模块实现（FInputBlueprintNodesModule）

模块启动时执行两个关键注册：

1. **资产拖拽支持**：通过 `FInputActionGraphActions` 注册 `UInputAction` 类的图操作，允许将 InputAction 资产拖入蓝图图表自动创建 `UK2Node_EnhancedInputAction` 节点。如果该 Action 的节点已存在，则跳转到已有节点。

2. **自动同步 Tick**：模块实现了 `FTickableEditorObject`，每帧检查 `UInputAction::ActionsWithModifiedValueTypes` 和 `UInputAction::ActionsWithModifiedTriggers` 集合。当用户修改 InputAction 的值类型或触发器时，自动重建所有引用该 Action 的蓝图节点，并弹出通知提示受影响的蓝图数量。

## 蓝图用法

### 核心节点

| 节点 | 菜单路径 | 说明 | 所在类 |
|---|---|---|---|
| EnhancedInputAction {ActionName} | Input > Enhanced Action Events | 输入动作事件，监听触发器事件 | `UK2Node_EnhancedInputAction` |
| Get {ActionName} | Input > Enhanced Action Values | 纯函数，获取当前输入动作值 | `UK2Node_GetInputActionValue` |
| Debug Key {Key} | Input > Debug Events > {Category} Events | 调试用键事件（DevelopmentOnly） | `UK2Node_InputDebugKey` |

### 使用示例（蓝图描述）

**监听输入动作事件：**

1. 在蓝图事件图表中右键，选择 "Input > Enhanced Action Events > 你的 Action 名称"
2. 节点会出现，默认显示 `Triggered` 执行引脚
3. 将 `Triggered` 引脚连接到你的逻辑（如 AddMovementInput）
4. 将 `ActionValue` 引脚连接到需要读取输入值的节点
5. 如需其他事件（如 `Started`、`Completed`），点击节点底部的展开箭头

**获取当前输入值：**

1. 在蓝图中右键，选择 "Input > Enhanced Action Values > 你的 Action 名称"
2. 产出一个"Get xxx"纯函数节点
3. 输出引脚类型自动匹配 Action 的 ValueType（Bool/Double/Vector2D/Vector3）
4. 可在 Tick 等任何地方调用，获取当前帧的输入值

**资产拖拽：**

直接从内容浏览器将 `UInputAction` 资产拖入蓝图图表，自动创建对应的事件节点。

## C++ 用法

### 头文件引入

```cpp
#include "K2Node_EnhancedInputAction.h"
#include "K2Node_GetInputActionValue.h"
```

### 模块依赖

从 `InputBlueprintNodes.Build.cs` 提取：

| 模块 | 依赖类型 | 用途 |
|---|---|---|
| `InputEditor` | Public | 输入编辑器公共接口 |
| `BlueprintGraph` | Private | 蓝图图表操作、资产图操作注册 |
| `Core` | Private | 核心基础库 |
| `CoreUObject` | Private | UObject 系统 |
| `Engine` | Private | 引擎核心（InputAction、UserWidget 等） |
| `EnhancedInput` | Private | Enhanced Input 运行时模块 |
| `GraphEditor` | Private | 图表编辑器 UI |
| `InputCore` | Private | 输入核心（FKey 等） |
| `KismetCompiler` | Private | 蓝图编译器（ExpandNode 等） |
| `PropertyEditor` | Private | 属性编辑器 |
| `Slate` / `SlateCore` | Private | UI 框架 |
| `UnrealEd` | Private | 编辑器基础 |
| `UMGEditor` | Private | UMG Widget 蓝图编辑器 |
| `UMG` | Private | UMG 运行时（UserWidget 等） |
| `DataValidation` | Private | 数据验证框架 |

### 自定义节点 Spawner 模式

该模块展示了如何为自定义 K2 事件节点实现"同 Action 不重复创建"的模式：

```cpp
// UInputActionEventNodeSpawner 的 Invoke 逻辑
UEdGraphNode* UInputActionEventNodeSpawner::Invoke(UEdGraph* ParentGraph, ...) const
{
    UBlueprint* Blueprint = FBlueprintEditorUtils::FindBlueprintForGraphChecked(ParentGraph);

    // 检查是否已有相同 Action 的节点
    if (UK2Node* PreExistingNode = FindExistingNode(Blueprint))
    {
        return PreExistingNode;  // 返回已有节点，编辑器会跳转到它
    }

    // 没有则创建新节点
    return Super::Invoke(ParentGraph, Bindings, Location);
}
```

### 值类型动态引脚

`UK2Node_GetInputActionValue` 展示了如何根据运行时数据动态确定引脚类型：

```cpp
// 根据 InputAction 的 ValueType 决定输出引脚类型
static const TMap<EInputActionValueType, FValueTypeData> ValueLookups =
{
    { EInputActionValueType::Boolean, FValueTypeData(UEdGraphSchema_K2::PC_Boolean) },
    { EInputActionValueType::Axis1D, FValueTypeData(UEdGraphSchema_K2::PC_Real, UEdGraphSchema_K2::PC_Double) },
    { EInputActionValueType::Axis2D, FValueTypeData(UEdGraphSchema_K2::PC_Struct, NAME_None, TBaseStructure<FVector2D>::Get()) },
    { EInputActionValueType::Axis3D, FValueTypeData(UEdGraphSchema_K2::PC_Struct, NAME_None, TBaseStructure<FVector>::Get()) },
};
```

## 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `enhancedInput.bp.bShouldWarnOnUnsupportedInputPin` | false | 当不受支持的引脚被连接时是否输出警告 |
| `enhancedInput.bp.ShouldValidateWidgetBlueprintSettings` | true | 是否在数据验证中检查 Widget 蓝图的 EI 设置 |

## 维护状态

### 近期更新

1. **2025-10-01** `17729ba87a22` — Add null check to avoid crashing on partially deleted input nodes
   - 修复已删除输入节点的空指针崩溃问题（UE-316813），防止部分删除的节点导致编辑器崩溃。

2. **2025-07-10** `9803c443cfab` — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files
   - 工具化批量添加内联生成宏，优化编译速度。

3. **2025-05-30** `52e3dac151e1` — Updated headers using UnrealCodeFixup for dllstorage
   - 工具化批量更新头文件，将 DLL 导出标记从类型移到方法/静态变量上。

### 维护评价

- **创建时间**：2022 年 3 月，随 Enhanced Input 插件一起创建
- **年龄**：约 4 年，属于较新的模块
- **更新频率**：近 6 个月内有实质性更新（空指针修复），说明仍在活跃维护
- **更新特点**：近期更新主要是编译优化和 bug 修复，核心功能稳定
- **模块类型**：UncookedOnly，仅在编辑器中加载，不影响运行时性能
- **推荐度**：✅ 推荐使用。这是 Enhanced Input 在蓝图中工作的基础模块，是 UE5 输入系统的官方蓝图集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputBlueprintNodes)
- [Enhanced Input 插件目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput)
- [官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)
- [测试用例（位于 InputEditor 模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor/Private/Tests)
