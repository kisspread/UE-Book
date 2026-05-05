# InputEditor 模块

> Editor 模块，为 Enhanced Input 插件提供编辑器集成：资产工厂、Details 面板自定义、编辑器内输入处理子系统，以及自动化测试框架。

## 模块信息

| 属性 | 值 |
|---|---|
| 所属插件 | Enhanced Input |
| 模块类型 | Editor |
| 源文件数 | 22（含 7 个测试文件） |
| 创建时间 | 2022-03-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor) | |

## 用途

InputEditor 是 Enhanced Input 插件的编辑器侧模块，解决了以下核心问题：

1. **资产创建**：在 Content Browser 中右键创建 `UInputAction` 和 `UInputMappingContext` 资产，并支持子类选择
2. **属性面板自定义**：为 IMC 的键映射数组、Action 的 Triggers/Modifiers、Developer Settings 提供丰富的 Details 面板 UI（拖拽排序、Combo Trigger 检测、CDO 默认值编辑等）
3. **编辑器内输入处理**：通过 `UEnhancedInputEditorSubsystem` 在编辑器非 PIE 状态下捕获和处理输入事件，使 Editor Utility 可以响应输入操作
4. **自动升级**：首次打开项目时自动将遗留输入系统（`UInputComponent` / `UPlayerInput`）升级为 Enhanced Input 版本
5. **名称验证**：对 Player Mappable Key 的映射名称进行唯一性和长度验证

## 源码结构

```
Source/InputEditor/
├── InputEditor.Build.cs                        # 模块构建配置
├── Public/
│   ├── InputEditorModule.h                     # 模块主类 + 资产工厂
│   ├── EnhancedInputEditorSubsystem.h          # 编辑器输入子系统
│   ├── EnhancedInputEditorProcessor.h          # Slate 输入预处理器
│   ├── EnhancedInputEditorSettings.h           # 编辑器设置（项目级 + 用户级）
│   └── EnhancedInputPlayerMappableNameValidator.h  # 映射名称验证器
├── Private/
│   ├── InputEditorModule.cpp                   # 模块启动/关闭 + 资产工厂实现
│   ├── EnhancedInputEditorSubsystem.cpp        # 子系统初始化、Tick、InputKey
│   ├── EnhancedInputEditorProcessor.cpp        # 键盘/鼠标/手柄事件捕获
│   ├── EnhancedInputEditorSettings.cpp         # 设置默认值
│   ├── EnhancedInputPlayerMappableNameValidator.cpp  # 名称验证逻辑
│   ├── InputCustomizations.h / .cpp            # Details 面板自定义
│   ├── ActionMappingDetails.h / .cpp           # IMC 映射数组的自定义节点构建器
│   └── Tests/
│       ├── InputTestFramework.h / .cpp         # BDD 风格测试框架
│       ├── InputSystemTest.cpp                 # 系统级测试（值匹配、映射查询、注入、事件转换）
│       ├── InputBindingTest.cpp                # 绑定逻辑测试（数字/模拟/多键）
│       ├── InputModifierTest.cpp               # Modifier 测试（Negate/Scalar/DeadZone/性能）
│       ├── InputTriggerTest.cpp                # Trigger 测试（Pressed/Down/Released/Hold/Tap/Chord）
│       ├── InputPlayerMappableKeysTests.cpp    # 玩家可重映射键测试
│       └── InputIntegrationTest.cpp            # 集成测试（Trigger + 完整输入栈）
```

## 关键类

### FInputEditorModule

模块主类，负责：

- 注册 `FAssetTypeActions_InputAction` 和 `FAssetTypeActions_InputContext` 到 Content Browser 的 "Input" 分类
- 注册 4 个 Property Type/Class Customization 到 PropertyEditor 模块
- 注册 Slate 样式集（SVG 图标）
- 监听 `OnMainFrameCreationFinished` 事件，自动将项目输入类升级为 Enhanced Input

```cpp
// 注册的自定义布局
PropertyModule.RegisterCustomPropertyTypeLayout(
    FInputMappingContextMappingData::StaticStruct()->GetFName(), ...);
PropertyModule.RegisterCustomPropertyTypeLayout(
    "EnhancedActionKeyMapping", ...);
PropertyModule.RegisterCustomClassLayout(
    UEnhancedInputDeveloperSettings::StaticClass()->GetFName(), ...);
PropertyModule.RegisterCustomPropertyTypeLayout(
    UPlayerMappableKeySettings::StaticClass()->GetFName(), ...);
```

### UEnhancedInputEditorSubsystem

`UEditorSubsystem` + `IEnhancedInputSubsystemInterface` + `FTickableGameObject` 的多重继承。在编辑器非 PIE 状态下提供完整的 Enhanced Input 处理能力。

**核心功能**：

| 函数 | 说明 |
|---|---|
| `StartConsumingInput()` | 开始捕获编辑器输入，注册 InputPreprocessor，添加默认映射上下文 |
| `StopConsumingInput()` | 停止捕获，移除默认映射上下文 |
| `PushInputComponent(UInputComponent*)` | 将 InputComponent 按优先级压入处理栈 |
| `PopInputComponent(UInputComponent*)` | 从栈中移除 InputComponent |
| `InputKey(FInputKeyEventArgs)` | 由 InputPreprocessor 调用，将键盘/鼠标事件传递给 PlayerInput |
| `IsConsumingInput()` | 查询当前是否正在处理输入（蓝图可用） |

**蓝图可用节点**：

| 节点 | 类型 | 说明 |
|---|---|---|
| `PushInputComponent` | BlueprintCallable | 将 InputComponent 压入编辑器输入栈 |
| `PopInputComponent` | BlueprintCallable | 从编辑器输入栈弹出 InputComponent |
| `StartConsumingInput` | BlueprintCallable | 开始在编辑器中消费输入 |
| `StopConsumingInput` | BlueprintCallable | 停止在编辑器中消费输入 |
| `IsConsumingInput` | BlueprintCallable, BlueprintPure | 查询是否正在消费输入 |

### FEnhancedInputEditorProcessor

实现 `IInputProcessor` 接口的 Slate 输入预处理器。拦截编辑器中的所有输入事件并转发给 `UEnhancedInputEditorSubsystem`。

**捕获的事件类型**：
- 键盘按下/释放（`HandleKeyDownEvent` / `HandleKeyUpEvent`）
- 模拟输入（`HandleAnalogInputEvent`）
- 鼠标移动/按下/释放/双击（各 `HandleMouse*` 方法）
- 鼠标滚轮/手势（`HandleMouseWheelOrGestureEvent`）

**设计特点**：所有 Handle 方法返回 `false`，不会拦截输入——其他 InputProcessor 仍然正常运行。

### 资产工厂

#### UInputMappingContext_Factory

创建 `UInputMappingContext` 资产。当存在子类时弹出类选择器。支持通过 `SetInitialActions()` 预填 InputAction 映射。

#### UInputAction_Factory

创建 `UInputAction` 资产。当存在子类时弹出类选择器。

### 属性自定义

#### FEnhancedActionMappingCustomization

IMC 中单条键映射（`FEnhancedActionKeyMapping`）的 Details 面板自定义：
- 自定义 Key 选择器（支持 Combo Trigger 自动禁用键选择）
- 删除映射按钮
- 展示关联 InputAction 上的 Triggers/Modifiers（只读，空时自动隐藏）
- Trigger 变更时自动更新 UI 状态

#### FActionMappingsNodeBuilderEx

IMC 映射数组的自定义节点构建器：
- 按 InputAction 分组显示映射
- 支持组级别和单条映射级别的拖拽排序
- 组内添加/删除映射
- 资产重命名时自动更新引用
- 支持从 InputAction 资产右键创建预填充的 IMC

#### FEnhancedInputDeveloperSettingsCustomization

Enhanced Input Developer Settings 的 Details 面板自定义：
- 收集所有原生和蓝图子类的 CDO（`UInputModifier` / `UInputTrigger`）
- 在 "Trigger Default Values" 和 "Modifier Default Values" 分类下展示
- 监听资产注册表变更，自动刷新

#### FPlayerMappableKeyChildSettingsCustomization

`UPlayerMappableKeySettings` 的名称字段自定义：
- 带验证的文本框（检查长度、唯一性）
- 验证通过 CVar `EnhancedInput.bEnableNameValidation` 控制

### 编辑器设置

#### UEnhancedInputEditorProjectSettings

项目级设置（`config = Input`），所有用户共享：

| 属性 | 说明 |
|---|---|
| `DefaultEditorInputClass` | 编辑器子系统使用的 PlayerInput 类，默认 `UEnhancedPlayerInput` |
| `DefaultMappingContexts` | 始终应用于编辑器子系统的默认映射上下文数组 |

#### UEnhancedInputEditorSettings

用户级设置（`config = EditorPerProjectUserSettings`）：

| 属性 | 说明 |
|---|---|
| `bLogAllInput` | 是否记录所有编辑器输入（调试用，会产生大量日志） |
| `bAutomaticallyStartConsumingInput` | 初始化时是否自动开始消费输入 |
| `VisibleEventPinsByDefault` | 蓝图中 Input Action 事件节点默认显示的事件引脚位掩码 |

### FEnhancedInputPlayerMappableNameValidator

继承 `FStringSetNameValidator`，对 Player Mappable Key 名称进行验证：
- 长度检查（不超过 `NAME_SIZE`）
- 唯一性检查（通过 `FInputEditorModule::IsMappingNameInUse` 遍历所有 `UPlayerMappableKeySettings` CDO）
- 错误消息中包含占用该名称的资产名

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 运行时核心模块（Public 依赖） |
| `ApplicationCore` | 平台输入设备映射 |
| `BlueprintGraph` | 蓝图节点支持 |
| `Core` / `CoreUObject` | 基础框架 |
| `DetailCustomizations` | 属性自定义基础设施 |
| `Engine` | 引擎核心 |
| `GraphEditor` | 图编辑器 |
| `InputCore` | 输入核心类型（FKey 等） |
| `KismetCompiler` | 蓝图编译器 |
| `PropertyEditor` | 属性编辑器框架 |
| `SharedSettingsWidgets` | 共享设置 UI |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器框架 |
| `AssetTools` | 资产创建工具 |
| `DeveloperSettings` | 开发者设置基类 |
| `EditorSubsystem` | 编辑器子系统基类 |
| `ToolMenus` | 菜单系统 |
| `ContentBrowser` | 内容浏览器集成 |
| `SourceControl` | 源代码管理（自动升级时 checkout 配置文件） |
| `GameplayTags` | Gameplay Tag 支持 |

## C++ 用法

### 头文件引入

```cpp
#include "InputEditorModule.h"                          // 模块主类 + 资产工厂
#include "EnhancedInputEditorSubsystem.h"               // 编辑器子系统
#include "EnhancedInputEditorProcessor.h"               // 输入预处理器
#include "EnhancedInputEditorSettings.h"                // 编辑器设置
```

### 在编辑器工具中使用输入子系统

```cpp
// 获取编辑器子系统实例
UEnhancedInputEditorSubsystem* EditorSubsystem = 
    GEditor->GetEditorSubsystem<UEnhancedInputEditorSubsystem>();

// 开始捕获输入（会自动添加默认映射上下文）
EditorSubsystem->StartConsumingInput();

// 推送你的 InputComponent
EditorSubsystem->PushInputComponent(MyInputComponent);

// 停止捕获
EditorSubsystem->StopConsumingInput();
```

### 创建 InputAction 资产（从代码）

```cpp
// 使用工厂创建
UInputAction_Factory* Factory = NewObject<UInputAction_Factory>();
UInputAction* NewAction = Cast<UInputAction>(
    Factory->FactoryCreateNew(
        UInputAction::StaticClass(), 
        ParentPackage, 
        FName("IA_MyAction"), 
        RF_Transactional, 
        nullptr, 
        GWarn));
```

### 从 InputAction 批量创建 IMC

```cpp
// 右键选中多个 InputAction 后，通过 FAssetTypeActions_InputAction 的
// "Create an Input Mapping Context" 上下文菜单操作
// 这会自动创建以 IMC_ 为前缀的映射上下文，并预填选中的 Actions
```

## 测试框架

InputEditor 模块内嵌了一套 BDD 风格的自动化测试框架。

### 测试基础设施

- `UControllablePlayer`：封装 PlayerController + EnhancedPlayerInput + EnhancedInputComponent + MockedSubsystem
- `UMockedEnhancedInputSubsystem`：无需创建完整游戏实例的 Mock 子系统
- `UInputBindingTarget`：记录委托触发结果的测试目标对象
- `FInputTestHelper`：提供事件检测和结果读取的静态辅助方法

### BDD 宏

```cpp
GIVEN(AnEmptyWorld());                                    // 前置条件
UControllablePlayer& Data = AND(AControllablePlayer(W));  // 附加条件
WHEN(AKeyIsActuated(Data, TestKey));                      // 操作
THEN(PressingKeyTriggersAction(Data, TestAction));        // 断言
ANDALSO(PressingKeyTriggersStarted(Data, TestAction));    // 附加断言
```

### 测试覆盖范围

| 测试文件 | 测试数量 | 覆盖内容 |
|---|---|---|
| `InputSystemTest.cpp` | 6 | 值类型匹配、配对轴、映射查询、输入注入、上下文注册追踪、事件转换 |
| `InputBindingTest.cpp` | 3 | 数字触发、模拟触发、多键值合并 |
| `InputModifierTest.cpp` | 5 | Negate、Scalar、DeadZone、UnscaledRadialDeadZone、性能基准 |
| `InputTriggerTest.cpp` | 7 | Pressed、Down、Released、Hold、HoldAndRelease、Tap、Chord（单/多上下文） |
| `InputPlayerMappableKeysTests.cpp` | 4 | IMC 注册/注销、键映射/取消映射、重置默认、多配置文件 |
| `InputIntegrationTest.cpp` | 4 | Pressed/Down/Released/Hold Trigger 的完整输入栈集成测试 |

### 关键 CVar

| CVar | 默认值 | 说明 |
|---|---|---|
| `EnhancedInput.bEnableAutoUpgrade` | true | 自动将遗留输入类升级为 Enhanced Input |
| `EnhancedInput.bEnableNameValidation` | true | 编辑器中对 Player Mappable Key 名称进行验证 |
| `EnhancedInput.Editor.EnableMappingNameValidation` | true | 映射名称验证开关 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-06-25 | `9664587` | 移除在 5.3 中已废弃的 `UPlayerMappableInputConfig` 类型 |
| 2025-06-25 | `8c4b054` | 为 `UInputMappingContext` 添加 `MappingProfileOverrides` 属性，支持不同 Key Profile 的默认键映射 |
| 2025-05-30 | `52e3dac` | 使用 UnrealCodeFixup 更新头文件，将 dllstorage 放到方法/静态变量上 |

### 维护评价

- **活跃维护**：最近 6 个月内有功能性更新（5.7 分支的 Profile 覆盖系统、废弃类型清理）
- **测试完善**：模块内含 7 个测试文件，覆盖系统级、绑定、Modifier、Trigger、玩家可重映射键、集成测试
- **Epic 官方维护**：作为 UE5 默认输入系统的核心编辑器模块，持续得到 Epic 的维护和更新
- **推荐使用**：这是 UE5 Enhanced Input 的标准编辑器模块，所有使用 Enhanced Input 的项目都依赖此模块

## 相关链接

- [源码（目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/EnhancedInput/Source/InputEditor/Private/Tests)
- [Enhanced Input 官方文档](https://docs.unrealengine.com/en-US/enhanced-input-in-unreal-engine/)
