
$weaponsDir = "c:\Users\menti\Desktop\novo-shard\Projects\UOContent\Items\Weapons"
$outputFile = "c:\Users\menti\Desktop\novo-shard\WeaponCalc\Weapon_Analysis_Report.json"

$results = @()

$files = Get-ChildItem -Path $weaponsDir -Filter "*.cs" -Recurse

foreach ($file in $files) {
    if ($file.Name -eq "BaseWeapon.cs" -or $file.Name -eq "BaseMeleeWeapon.cs" -or $file.Name -eq "BaseSword.cs") { continue }
    
    $content = Get-Content $file.FullName -Raw
    
    # Extract Weapon Name
    if ($content -match "public( partial)? class (\w+)") {
        $name = $matches[2]
    }
    else {
        continue
    }

    # Extract Stats via Regex
    $oldMin = if ($content -match "(?m)^\s+public override int OldMinDamage => (\d+);") { [int]$matches[1] } else { 0 }
    $oldMax = if ($content -match "(?m)^\s+public override int OldMaxDamage => (\d+);") { [int]$matches[1] } else { 0 }
    $oldSpeed = if ($content -match "(?m)^\s+public override int OldSpeed => (\d+);") { [int]$matches[1] } else { 0 }
    $sphereSpeed = if ($content -match "(?m)^\s+public override int SphereSpeed => (\d+);") { [int]$matches[1] } else { 0 }
    
    $aosMin = if ($content -match "(?m)^\s+public override int AosMinDamage => (\d+);") { [int]$matches[1] } else { 0 }
    $aosMax = if ($content -match "(?m)^\s+public override int AosMaxDamage => (\d+);") { [int]$matches[1] } else { 0 }

    # Find Base Class
    $baseClass = ""
    if ($content -match "(?m)^.*class (\w+)\s*:\s*(\w+)") {
        $baseClass = $matches[2]
    }

    # Map Category based on baseClass
    $skill = "Swords" # Default
    if ($baseClass -match "BaseBashing|BaseStaff|Mace|Hammer|Club|Crook|Wand") {
        $skill = "Maces"
    }
    elseif ($baseClass -match "BaseSword|BaseAxe|BasePoleArm|Axe|Halberd|Bardiche|Scythe") {
        $skill = "Swords"
    }
    elseif ($baseClass -match "BaseSpear|Dagger|Kryss|Pike|Fork") {
        $skill = "Fencing"
    }
    elseif ($baseClass -match "BaseRanged|BaseBow|Crossbow|Bow") {
        $skill = "Bows"
    }
    elseif ($baseClass -match "BaseThrowing|Boomerang|Cyclone|SoulGlaive") {
        $skill = "Throwing"
    }

    # Override if explicitly defined in class, but only if it's more specific
    if ($content -match "(?m)^\s+public override SkillName(?: OldSkill| DefSkill) => SkillName\.(\w+);") {
        $explicitSkill = $matches[1]
        if ($explicitSkill -eq "Macing") { $skill = "Maces" }
        if ($explicitSkill -eq "Swords") { $skill = "Swords" }
        if ($explicitSkill -eq "Fencing") { $skill = "Fencing" }
        if ($explicitSkill -eq "Archery") { $skill = "Bows" }
    }

    $layer = "OneHanded" # Default
    if ($content -match "(?m)Layer(( \= )|\.)(OneHanded|TwoHanded)") {
        $layer = $matches[3]
    }
    elseif ($content -match "(?m)base\((\s+)?(?:0x[0-9a-fA-F]+)\)") {
        # Try to look at base constructor if we don't have layer? Usually it's in base class but let's try to parse if there's explicit layer setting
        if ($content -match "(?m)Layer \= Layer\.TwoHanded") { $layer = "TwoHanded" }
    }
    
    # Heuristics for typical two handed weapons if layer isn't explicitly set in the final class
    $twoHandedNames = @("Halberd", "Bardiche", "Axe", "BattleAxe", "DoubleAxe", "ExecutionersAxe", "LargeBattleAxe", "TwoHandedAxe", "Bow", "Crossbow", "HeavyCrossbow", "CompositeBow", "RepeatingCrossbow", "BlackStaff", "GnarledStaff", "QuarterStaff", "Spear", "ShortSpear", "Pitchfork")
    if ($twoHandedNames -contains $name) {
        $layer = "TwoHanded"
    }

    # Calculate Swing Speed in seconds (100 Dex)
    $baseSpeed = if ($sphereSpeed -gt 0) { $sphereSpeed } else { $oldSpeed }
    $calculatedSpeed = ($baseSpeed / 100.0) * 0.65

    $results += [PSCustomObject]@{
        Name         = $name
        OldMin       = $oldMin
        OldMax       = $oldMax
        AosMin       = $aosMin
        AosMax       = $aosMax
        SphereSpeed  = $sphereSpeed
        OldSpeed     = $oldSpeed
        SwingSeconds = $calculatedSpeed
        Skill        = $skill
        Layer        = $layer
    }
}

$results | ConvertTo-Json -Compress | Out-File $outputFile -Encoding utf8
Write-Output "JSON data generated at $outputFile"
