<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" version="1.1.0" xmlns:se="http://www.opengis.net/se" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <se:Name>Hydrogeol_poly</se:Name>
    <UserStyle>
      <se:Name>Hydrogeol_poly</se:Name>
      <se:FeatureTypeStyle>
        <se:Rule>
          <se:Name>Terrigenous, lightly cemented interrupted rocks: alternation of clays, sandstones and conglomerates</se:Name>
          <se:Description>
            <se:Title>Terrigenous, lightly cemented interrupted rocks: alternation of clays, sandstones and conglomerates</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>Terrigenous, lightly cemented interrupted rocks: alternation of clays, sandstones and conglomerates</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#f4f147</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Terrigenous loose clastic, lake-river and continental sediments: boulders, pebbles, sand, sandy loam, clay alternating with andesite-basalt streams and nappes in intermountain basins</se:Name>
          <se:Description>
            <se:Title>Terrigenous loose clastic, lake-river and continental sediments: boulders, pebbles, sand, sandy loam, clay alternating with andesite-basalt streams and nappes in intermountain basins</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>Terrigenous loose clastic, lake-river and continental sediments: boulders, pebbles, sand, sandy loam, clay alternating with andesite-basalt streams and nappes in intermountain basins</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#edc7ea</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Mainly in carbonate rocks, in some places alternated with terrigenous formations: limestones, marls, dolomites, quartzites, limy sandstones, tuffs and conglomerates</se:Name>
          <se:Description>
            <se:Title>Mainly in carbonate rocks, in some places alternated with terrigenous formations: limestones, marls, dolomites, quartzites, limy sandstones, tuffs and conglomerates</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>Mainly in carbonate rocks, in some places alternated with terrigenous formations: limestones, marls, dolomites, quartzites, limy sandstones, tuffs and conglomerates</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#b289df</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Mainly in volcanogenic-sedimentary rocks: tuff-sandstones, tuff-gravelites, tuff-conglomerates and tuffites, in some places alternated with limestone and clay shales</se:Name>
          <se:Description>
            <se:Title>Mainly in volcanogenic-sedimentary rocks: tuff-sandstones, tuff-gravelites, tuff-conglomerates and tuffites, in some places alternated with limestone and clay shales</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>Mainly in volcanogenic-sedimentary rocks: tuff-sandstones, tuff-gravelites, tuff-conglomerates and tuffites, in some places alternated with limestone and clay shales</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#dfd5a6</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>In volcanic lavas: basalts, andesite-basalts,andesites, andesite-dacites, dacites</se:Name>
          <se:Description>
            <se:Title>In volcanic lavas: basalts, andesite-basalts,andesites, andesite-dacites, dacites</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>In volcanic lavas: basalts, andesite-basalts,andesites, andesite-dacites, dacites</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#aec588</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>In pyroclastic variations of lavas: ash-pumice tuffs, tuff-lavas, riolites, obsidians, slags, pumices and volcanic sands</se:Name>
          <se:Description>
            <se:Title>In pyroclastic variations of lavas: ash-pumice tuffs, tuff-lavas, riolites, obsidians, slags, pumices and volcanic sands</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>In pyroclastic variations of lavas: ash-pumice tuffs, tuff-lavas, riolites, obsidians, slags, pumices and volcanic sands</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#bccf11</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Mainly in volcanogenic rocks: porphyrities, diabases, keratophyries and their pyroclasts</se:Name>
          <se:Description>
            <se:Title>Mainly in volcanogenic rocks: porphyrities, diabases, keratophyries and their pyroclasts</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>Mainly in volcanogenic rocks: porphyrities, diabases, keratophyries and their pyroclasts</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#f48000</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>In metamorphic shales</se:Name>
          <se:Description>
            <se:Title>In metamorphic shales</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>In metamorphic shales</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#eeb378</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>In intrusive rocks of acid, basic and ultrabasic composition</se:Name>
          <se:Description>
            <se:Title>In intrusive rocks of acid, basic and ultrabasic composition</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>In intrusive rocks of acid, basic and ultrabasic composition</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#ed3cdf</se:SvgParameter>
            </se:Fill>
          </se:PolygonSymbolizer>
        </se:Rule>
        <se:Rule>
          <se:Name>Main lakes and reservoirs</se:Name>
          <se:Description>
            <se:Title>Main lakes and reservoirs</se:Title>
          </se:Description>
          <ogc:Filter xmlns:ogc="http://www.opengis.net/ogc">
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>Aquifer</ogc:PropertyName>
              <ogc:Literal>Main lakes and reservoirs</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <se:PolygonSymbolizer>
            <se:Fill>
              <se:SvgParameter name="fill">#5fb1f4</se:SvgParameter>
            </se:Fill>
            <se:Stroke>
              <se:SvgParameter name="stroke">#265980</se:SvgParameter>
              <se:SvgParameter name="stroke-width">1</se:SvgParameter>
              <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
            </se:Stroke>
          </se:PolygonSymbolizer>
        </se:Rule>
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
