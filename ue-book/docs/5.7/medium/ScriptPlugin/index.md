# Script Plugin

> An example of a script plugin. This can be used as a starting point when creating your own plugin.

| 属性 | 值 |
|---|---|
| 分类 | Examples |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ScriptPlugin` (Runtime), `ScriptEditorPlugin` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-04-29 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ScriptPlugin) | |

## 用途

ScriptPlugin 是 Epic 提供的**脚本语言集成示例插件**，展示了如何在 UE5 中嵌入外部脚本语言（当前实现为 Lua）。它不是一个生产级的 Lua 绑定方案（那是 UnrealLua / slua-unreal 等第三方插件的工作），而是一个**参考实现和教学模板**，帮助开发者理解：

- 如何通过 `FScriptContextBase` 抽象接口对接任意脚本语言运行时
- 如何将脚本定义的变量和函数暴露为 Blueprint 可用的属性和事件
- 如何通过 UBT (Unreal Build Tool) 的 UHT Exporter 自动生成 C++ ↔ 脚本的绑定代码
- 如何为自定义资产类型（ScriptBlueprint）实现编辑器导入/重导入/编译的完整工作流

插件的核心架构是 **Script Context 模式**：每个挂载了脚本的 Actor 或 Component 内部持有一个 `FScriptContextBase*`，在 `Initialize`、`BeginPlay`、`Tick`、`Destroy` 等生命周期节点自动同步 C++ 属性值到脚本环境，并调用脚本端对应的函数。

## 使用场景

- 你想学习如何为 UE5 编写自定义脚本语言插件 → 阅读 ScriptPlugin 源码作为起点
- 你需要一个简单的 Lua 集成方案用于原型验证 → 启用此插件并手动编译 Lua 库
- 你想理解 Blueprint 编译器如何支持非原生代码生成的类 → 研究 `FScriptBlueprintCompiler`
- 你想了解 UHT Exporter 如何自动生成绑定代码 → 研究 `ScriptGeneratorUbtPlugin`

**注意**：此插件默认禁用（`EnabledByDefault=false`），且不支持 Linux 平台。生产环境推荐使用 UnrealLua、slua-unreal 或 Unreal.js 等成熟方案。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CallScriptFunction` | 调用脚本中定义的无参函数，自动同步属性 | `UScriptContext` |
| `CallScriptFunction` | 调用脚本中定义的无参函数，自动同步属性 | `UScriptPluginComponent` |
| `CallScriptFunction` | 调用脚本中定义的无参函数，自动同步属性 | `UScriptContextComponent` |

### 使用示例（蓝图描述）

**方式一：基于 Actor 的脚本类**

1. 导入一个 `.lua` 文件到 Content Browser（需要先启用插件并编译 Lua 库）
2. 导入时选择父类为 `AActor`（或其子类）
3. 编辑器会创建一个 `ScriptBlueprint` 资产
4. 打开 ScriptBlueprint，在 Defaults 面板中可以看到 Lua 脚本中定义的变量
5. 将 ScriptBlueprint 拖入场景，运行时 Lua 脚本会自动执行 `BeginPlay` 和 `Tick`

**方式二：基于 Component 的脚本扩展**

1. 创建一个继承 `UScriptPluginComponent` 的 ScriptBlueprint（导入 `.lua` 时选择父类）
2. 将该组件添加到任意 Actor
3. 组件在 `OnRegister` 时创建 Lua 上下文，`InitializeComponent` 时调用 `BeginPlay`
4. 每帧 `TickComponent` 会同步属性并调用 Lua 端的 `Tick` 函数

**方式三：蓝图中手动调用脚本函数**

在蓝图中：
1. 获取 Actor 上的 `UScriptContextComponent` 引用
2. 调用 `CallScriptFunction` 节点，传入函数名字符串（如 `"MyLuaFunction"`）
3. 调用前后会自动同步所有脚本定义的属性

## C++ 用法

### 头文件引入

```cpp
#include "ScriptBlueprintGeneratedClass.h"  // FScriptContextBase, FScriptField, UScriptBlueprintGeneratedClass
#include "ScriptPluginComponent.h"           // UScriptPluginComponent
#include "ScriptContextComponent.h"          // UScriptContextComponent
#include "ScriptContext.h"                   // UScriptContext
#include "ScriptBlueprint.h"                // UScriptBlueprint
```

### 基本用法：理解 Script Context 架构

ScriptPlugin 的核心是 `FScriptContextBase` 抽象类，定义了脚本运行时的完整接口：

```cpp
// 来源: Source/ScriptPlugin/Classes/ScriptBlueprintGeneratedClass.h

class FScriptContextBase
{
public:
    // 工厂方法：根据 WITH_LUA 宏决定创建 FLuaContext 还是返回 NULL
    static FScriptContextBase* CreateContext(
        const FString& SourceCode,
        UScriptBlueprintGeneratedClass* Class,
        UObject* Owner);

    // 生命周期
    virtual bool Initialize(const FString& Code, UObject* Owner) = 0;
    virtual void BeginPlay() = 0;
    virtual void Tick(float DeltaTime) = 0;
    virtual void Destroy() = 0;
    virtual bool CanTick() = 0;

    // 函数调用
    virtual bool CallFunction(const FString& FunctionName) = 0;

    // 属性读写（支持 float/int/object/bool/string）
    virtual bool SetFloatProperty(const FString& PropertyName, float NewValue) = 0;
    virtual float GetFloatProperty(const FString& PropertyName) = 0;
    // ... 其他类型类似

    // 属性同步工具方法
    virtual void PushScriptPropertyValues(UScriptBlueprintGeneratedClass* Class, const UObject* Obj);
    virtual void FetchScriptPropertyValues(UScriptBlueprintGeneratedClass* Class, UObject* Obj);
};
```

### 基本用法：属性同步机制

`PushScriptPropertyValues` 和 `FetchScriptPropertyValues` 是属性双向同步的核心：

```cpp
// 来源: Source/ScriptPlugin/Private/ScriptBlueprintGeneratedClass.cpp

void FScriptContextBase::PushScriptPropertyValues(UScriptBlueprintGeneratedClass* Class, const UObject* Obj)
{
    // 遍历脚本定义的所有属性，从 C++ 对象推送到脚本环境
    for (TFieldPath<FProperty>& Property : Class->ScriptProperties)
    {
        if (FFloatProperty* FloatProperty = CastField<FFloatProperty>(Property.Get()))
        {
            float Value = FloatProperty->GetFloatingPointPropertyValue(
                Property->ContainerPtrToValuePtr<float>(Obj));
            SetFloatProperty(Property->GetName(), Value);
        }
        else if (FIntProperty* IntProperty = CastField<FIntProperty>(Property.Get()))
        {
            int32 Value = IntProperty->GetSignedIntPropertyValue(
                Property->ContainerPtrToValuePtr<int32>(Obj));
            SetIntProperty(Property->GetName(), Value);
        }
        // ... bool, object, string 类似处理
    }
}
```

### 进阶用法：Lua 集成细节

当 `WITH_LUA=1` 时，`FLuaContext` 提供完整的 Lua 5.3 运行时集成：

```cpp
// 来源: Source/ScriptPlugin/Private/LuaIntegration.cpp

bool FLuaContext::Initialize(const FString& Code, UObject* Owner)
{
    LuaState = LuaNewState();                    // 使用 FMemory 分配器创建 Lua 状态
    luaL_openlibs(LuaState);                      // 打开标准库
    LuaRegisterExportedClasses(LuaState);         // 注册 UHT 生成的绑定
    LuaRegisterUnrealUtilities(LuaState);         // 注册 UE 工具库（UE, Transform）

    // 加载并执行脚本
    if (luaL_loadstring(LuaState, TCHAR_TO_ANSI(*Code)) == 0)
    {
        // 设置 'this' 全局变量指向 Owner UObject
        lua_pushlightuserdata(LuaState, Owner);
        lua_setglobal(LuaState, "this");

        FLuaUtils::CallFunction(LuaState, NULL);

        // 检测脚本是否定义了生命周期函数
        bHasTick = FLuaUtils::DoesFunctionExist(LuaState, "Tick");
        bHasDestroy = FLuaUtils::DoesFunctionExist(LuaState, "Destroy");
        bHasBeginPlay = FLuaUtils::DoesFunctionExist(LuaState, "BeginPlay");
    }
    return bResult;
}
```

Lua 脚本中可直接使用的全局 API：

```lua
-- 全局变量 'this' 指向当前 Owner UObject（lightuserdata）

-- UObject 工具函数（注册在 UE 表中）
local obj = UE.FindObject(nil, nil, "/Game/MyAsset")
local name = UE.GetName(obj)
local valid = UE.IsValid(obj)

-- 生命周期函数（可选定义）
function BeginPlay()     -- 组件初始化时调用
function Tick()          -- 每帧调用（定义此函数才会启用 Tick）
function Destroy()       -- 销毁时调用

-- print 被重定向到 UE_LOG
print("Hello from Lua!")
```

### 进阶用法：UHT 代码生成

`ScriptGeneratorUbtPlugin` 是一个 UBT 插件（C#），在 UHT 阶段自动为标记了 `RequiredAPI` 或 `MinimalAPI` 的类生成脚本绑定代码：

```csharp
// 来源: Source/ScriptGeneratorUbtPlugin/ScriptGenerator.cs

[UhtExporter(Name = "ScriptPlugin", Description = "Generic Script Plugin Generator",
    Options = UhtExporterOptions.Default, ModuleName = "ScriptPlugin")]
private static void ScriptGeneratorExporter(IUhtExportFactory Factory)
{
    if (Factory.PluginModule != null)
    {
        int Value;
        if (Factory.PluginModule.TryGetDefine("WITH_LUA", out Value))
        {
            if (Value == 0)
                new GenericScriptCodeGenerator(Factory).Generate();  // 通用绑定
            else
                new LuaScriptCodeGenerator(Factory).Generate();      // Lua 专用绑定
        }
    }
}
```

Lua 绑定为每个导出类生成：
- `ClassName_New(lua_State*)` — 创建新对象
- `ClassName_Destroy(lua_State*)` — 销毁对象
- `ClassName_Class(lua_State*)` — 获取 UClass
- `ClassName_FunctionName(lua_State*)` — 每个 UFUNCTION 的包装
- `ClassName_Get_PropertyName / Set_PropertyName` — 每个 UPROPERTY 的 getter/setter
- 一个 `luaL_Reg` 数组注册所有函数到 Lua 全局表

## Demo 示例

### Lua 脚本示例：旋转方块

创建文件 `RotateCube.lua`：

```lua
-- 旋转方块示例
-- 定义脚本属性（会被编译器识别为 Blueprint 可编辑属性）
RotationSpeed = 90.0
CurrentAngle = 0.0

function BeginPlay()
    print("RotateCube BeginPlay! Speed = " .. RotationSpeed)
end

function Tick()
    CurrentAngle = CurrentAngle + RotationSpeed * 0.016  -- 假设 ~60fps
    -- 注意：需要通过 UHT 生成的绑定来操作 Actor 的 Rotation
    -- 这里仅演示脚本属性的自动同步
end

function Destroy()
    print("RotateCube Destroy!")
end
```

### 使用此插件的 Build.cs 依赖

```csharp
// 你的模块 Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "ScriptPlugin"  // 依赖 ScriptPlugin 模块
});
```

### 启用 Lua 集成的步骤

1. 下载 Lua 5.3.0 源码，解压到 `Engine/Plugins/ScriptPlugin/Source/Lua/lua-5.3.0/`
2. 用 Visual Studio 打开 `Engine/Plugins/ScriptPlugin/Source/Lua/Lua.sln`
3. 编译 Release Win32 和 Release x64 配置
4. 运行 `GenerateProjectFiles.bat` 重新生成项目文件
5. 重新编译引擎

编译时 `ScriptPlugin.Build.cs` 会检测 `Lua.lib` 是否存在，存在则定义 `WITH_LUA=1`。

## 模块依赖

### ScriptPlugin (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、内存管理、日志 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | Actor、Component、World |
| `InputCore` | 输入系统基础类型 |
| `SlateCore` | Slate UI 基础类型 |
| `EditorFramework` | 编辑器框架（仅编辑器构建） |
| `UnrealEd` | 编辑器工具（仅编辑器构建） |

### ScriptEditorPlugin (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器工具 |
| `AssetTools` | 资产导入/管理 |
| `ScriptPlugin` | 运行时模块（ScriptContext 等） |
| `ClassViewer` | 类选择器对话框 |
| `KismetCompiler` | Blueprint 编译器框架 |
| `Kismet` | Blueprint 编辑器 |
| `BlueprintGraph` | Blueprint 图节点 |

## 维护状态

### 近期更新

1. `185bf17020e4` | 2025-06-13 | Replace some usages of FORCEINLINE with inline in Engine modules.
   - 代码风格统一：将 `FORCEINLINE` 替换为 `inline`，无功能变化。

2. `269aeb1b3363` | 2025-05-21 | Replaced bool arguments with EFindObjectFlags.
   - API 适配：Lua 集成中的 `StaticFindObject` / `StaticFindObjectFast` 调用更新为使用 `EFindObjectFlags` 枚举。

3. `216a397b1dde` | 2025-03-03 | Added new IUhtExportFactory methods, GetModuleShortestIncludePath and GetPluginShortestIncludePath.
   - UBT 适配：代码生成器使用新的 `GetPluginShortestIncludePath` API。

### 维护评价

ScriptPlugin 自 2014 年创建以来已超过 12 年，是一个典型的**教学/示例性质插件**。最近的更新全部是编译适配性修改（跟随引擎 API 变化），没有任何功能性增强。

**关键判断**：
- ⚠️ **不推荐直接用于生产** — 插件本身标注为 "example"，功能有限
- ⚠️ **Lua 集成需要手动编译** — 不附带预编译的 Lua 库
- ⚠️ **不支持 Linux** — `PlatformDenyList` 包含 Linux
- ⚠️ **仅支持基础类型** — 不支持 Array、Delegate、WeakObjectPtr 等复杂类型
- ⚠️ **单向属性同步** — 属性同步是 Push/Fetch 模式，非实时绑定
- ✅ **仍有编译维护** — 跟随引擎 API 变化更新，不会编译失败
- ✅ **架构设计优秀** — 适合作为编写自定义脚本插件的参考

**推荐用法**：将其作为学习材料和脚手架代码，在此基础上开发自己的脚本语言集成方案。生产环境请使用 UnrealLua、slua-unreal、Unreal.js 等成熟方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ScriptPlugin)
- 官方文档（无）
- Lua 源码目录: `Engine/Plugins/ScriptPlugin/Source/Lua/`（需自行下载 Lua 5.3.0）
