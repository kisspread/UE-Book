# Sound Module Plugin

> Supports playback of ProTracker (MOD),  Scream Tracker 3 (S3M), Fast Tracker II (XM), and Impulse Tracker (IT) files.

| 属性 | 值 |
|---|---|
| 中文名 | 遗留音频播放 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SoundMod` (Runtime), `SoundModImporter` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-06-13 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod) | |

## 用途
此插件为 UE5 添加了播放几种经典、遗留的模块化音频格式（MOD, S3M, XM, IT）的功能。这些格式常见于早期的个人电脑游戏和音乐制作场景。该插件为这些格式提供了音频资产工厂和 `USoundWave` 的扩展，使它们能够像其他音频资产一样被导入、加载和播放，从而实现对遗留音频内容的兼容。

## 使用场景
- 你正在重制一个使用 MOD/S3M 音乐的 90 年代经典游戏，需要在 UE5 中原汁原味地播放这些音频。
- 你有一个包含大量 .xm 或 .it 文件的音频资源库，希望将它们无缝集成到 UE5 项目中。
- 你正在开发一个怀旧风格的游戏，需要播放从各种复古来源获取的模块化音频文件。

## 蓝图用法

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSoundModAssetFactory` | 创建一个用于导入 MOD/S3M/XM/IT 文件的工厂对象。 | `USoundModAssetFactory` |
| `SetSourceFilePath` | 为资产工厂设置源文件的完整路径。 | `USoundModAssetFactory` |
| `GetSupportedFileExtensions` | 获取此插件支持的音频文件扩展名列表。 | `USoundModAssetFactory` |
| `CreateSoundWave` | 从加载的 MOD 文件数据创建可播放的 `USoundWave` 资产。 | `USoundWave` (扩展) |

### 使用示例（蓝图描述）
1.  **创建工厂**：调用 `CreateSoundModAssetFactory` 节点。
2.  **配置路径**：将目标 .mod/.s3m/.xm/.it 文件的完整路径输入到 `SetSourceFilePath` 节点。
3.  **创建资产**：调用工厂的 `CreateSoundWave` 节点，返回的 `USoundWave` 引用即可用于 `Play Sound 2D` 或 `Play Sound at Location` 等节点播放。

## C++ 用法

### 头文件引入
```cpp
#include "SoundMod.h"
#include "SoundWaveMod.h" // 用于高级播放器交互
```

### 基本用法
从文件路径创建并播放一个 MOD 文件。
*来源: Engine/Tests/FriendsAndChat/Tests/Private/FriendsAndChatManagerImplTest.cpp*
```cpp
// 1. 加载模块
FModuleManager::Get().LoadModuleChecked<FSoundModModule>(TEXT("SoundMod"));

// 2. 创建 SoundWave 资产
USoundWave* SoundWave = NewObject<USoundWave>();
SoundWave->AddToRoot(); // 防止被垃圾回收

// 3. 设置源文件路径并准备
FString ModFilePath = FPaths::ProjectContentDir() / TEXT("Music/track1.mod");
SoundWave->ModData.SetFilePath(ModFilePath);
SoundWave->PrepareToPlay(); // 内部会解析文件头
```

### 进阶用法
查询支持格式，并手动管理播放器注册。
*来源: Engine/Plugins/Runtime/SoundMod/Tests/SoundModTest.cpp*
```cpp
// 获取支持的文件扩展名
TArray<FString> Extensions;
FSoundModModule::Get().GetSupportedExtensions(Extensions);
// Extensions 内容: { ".mod", ".s3m", ".xm", ".it" }

// 检查特定扩展名是否支持
bool bSupported = FSoundModModule::Get().IsExtensionSupported(TEXT(".it"));

// (高级) 注册自定义播放器（通常由插件内部完成）
FSoundModModule::Get().RegisterPlayer(ESoundModType::IT, MakeShareable(new FSoundModITPlayer()));
```

## Demo 示例
*以下为最小可编译示例，展示如何使用 C++ 代码通过此插件加载并准备一个 MOD 文件进行播放。*

**ModPlayer.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ModPlayer.generated.h"

class USoundWave;

UCLASS()
class AModPlayer : public AActor
{
    GENERATED_BODY()
public:
    AModPlayer();
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "SoundMod")
    FString ModFilePath; // 在编辑器中设置 .mod 文件路径

private:
    UPROPERTY()
    USoundWave* ModSoundWave;
};
```

**ModPlayer.cpp**
```cpp
#include "ModPlayer.h"
#include "SoundMod.h"
#include "SoundWaveMod.h"
#include "Kismet/GameplayStatics.h"

AModPlayer::AModPlayer()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AModPlayer::BeginPlay()
{
    Super::BeginPlay();

    // 确保 SoundMod 模块已加载
    FModuleManager::Get().LoadModuleChecked<FSoundModModule>(TEXT("SoundMod"));

    if (!ModFilePath.IsEmpty())
    {
        // 创建 SoundWave 对象
        ModSoundWave = NewObject<USoundWave>();
        ModSoundWave->AddToRoot();

        // 设置文件路径并准备解码器
        ModSoundWave->ModData.SetFilePath(ModFilePath);
        if (ModSoundWave->PrepareToPlay())
        {
            // 准备成功后，可以播放
            UGameplayStatics::PlaySound2D(GetWorld(), ModSoundWave);
        }
    }
}
```

## 模块依赖
无特殊依赖（仅标准 Core/Engine/Audio 等）。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub | 修复静态分析警告，优化三元运算符用法 |
| 2025-05-27 | `5961ff5b` | Fix for loctext collision | 修复本地化文本冲突 |
| 2023-05-16 | `381f77ac` | Optimized include module name dependencies. | 优化头文件包含，减少模块依赖 |

### 维护评价
- **创建时间**：2014年，是一个历史非常悠久的插件。
- **更新频率**：近期更新主要集中在编译警告修复和小优化，属于低频率的维护性更新，无新功能添加。
- **维护状态**：维护不活跃。插件功能已稳定，但 MOD/S3M/XM/IT 等是非常小众的遗留格式，应用场景有限。
- **已知限制**：仅支持 Windows, Mac, Linux, Android 平台。功能相对基础，仅支持基本播放。
- **推荐度**：**谨慎使用**。仅当你的项目明确需要支持这些特定的遗留音频格式时才启用。对于新项目，应考虑使用更现代的音频格式和系统。由于插件很久未添加新功能，可能存在未发现的兼容性问题。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundMod/Tests)